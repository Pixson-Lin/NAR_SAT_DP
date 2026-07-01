"""GNSS 設備 log 解析（一台 NE → GPS / GLONASS 兩列）。"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

MAX_SIGNALS = 16
SIGNAL_PAD = "-"
CONSTELLATIONS = ("GPS", "GLONASS")

BEGIN_RE = re.compile(r"^\[BEGIN\]\s*(.+)$", re.MULTILINE)
HOSTNAME_RE = re.compile(r"^A:([^#]+)#", re.MULTILINE)
SAT_ROW_RE = re.compile(r"^(GPS|GLONASS)\s+\S+\s+\S+\s+(\d+)\s*$")
USED_TOTAL_RE = re.compile(r"No\.\s*of Used Satellites:\s*(\d+)")
ELEV_RE = re.compile(r"Elev\.\s*Mask Angle\s*:\s*(\d+)")


@dataclass
class GnssDump:
    signals: dict[str, list[int]] = field(default_factory=lambda: {c: [] for c in CONSTELLATIONS})
    total_used: int = 0


@dataclass
class GnssRow:
    source_archive: str = ""
    source_txt_path: str = ""
    hostname: str = ""
    control: str = ""
    elev_mask_angle: str = ""
    used_satellite_control: str = ""
    constellation: str = ""
    used_satellite_constellation: str = ""
    a_signals: list[str] = field(default_factory=list)
    b_signals: list[str] = field(default_factory=list)
    script_begin_time: str = ""

    def to_flat_dict(self) -> dict[str, str]:
        row = {
            "hostname": self.hostname,
            "Control": self.control,
            "Elev. Mask Angle": self.elev_mask_angle,
            "Used Satellite(Control)": self.used_satellite_control,
            "Constellation": self.constellation,
            "Used Satellite(Constellation)": self.used_satellite_constellation,
            "script_begin_time": self.script_begin_time,
        }
        if self.source_archive:
            row["source_archive"] = self.source_archive
        if self.source_txt_path:
            row["source_txt_path"] = self.source_txt_path
        for i in range(1, MAX_SIGNALS + 1):
            row[f"A signal {i}"] = self.a_signals[i - 1]
            row[f"B signal {i}"] = self.b_signals[i - 1]
        return row


def parse_begin_timestamp(text: str) -> str:
    """取第一個 hostname 之前最後一個 [BEGIN] 行的時間字串。"""
    first_host = HOSTNAME_RE.search(text)
    prefix = text[: first_host.start()] if first_host else text
    begin_time = ""
    for line in prefix.splitlines():
        stripped = line.strip()
        if stripped.startswith("[BEGIN]"):
            begin_time = stripped[len("[BEGIN]") :].strip()
    return begin_time


def parse_hostname(text: str) -> str:
    match = HOSTNAME_RE.search(text)
    if not match:
        raise ValueError("找不到 hostname（預期格式 A:{hostname}#）")
    return match.group(1).strip()


def _extract_between(text: str, start_marker: str, end_markers: list[str]) -> str:
    start = text.find(start_marker)
    if start < 0:
        raise ValueError(f"找不到區段: {start_marker!r}")
    start += len(start_marker)
    end = len(text)
    for marker in end_markers:
        pos = text.find(marker, start)
        if pos >= 0:
            end = min(end, pos)
    return text[start:end]


def parse_dump_block(block: str) -> GnssDump:
    signals: dict[str, list[int]] = {c: [] for c in CONSTELLATIONS}
    for line in block.splitlines():
        match = SAT_ROW_RE.match(line.strip())
        if not match:
            continue
        constellation = match.group(1)
        if constellation in signals:
            signals[constellation].append(int(match.group(2)))
    total_match = USED_TOTAL_RE.search(block)
    total_used = int(total_match.group(1)) if total_match else sum(len(v) for v in signals.values())
    return GnssDump(signals=signals, total_used=total_used)


def parse_elev_mask_angles(text: str) -> dict[str, str]:
    show_a = _extract_between(
        text,
        'show port a/gnss | match "Angle     :"',
        ['show port b/gnss | match "Angle     :"', "logout"],
    )
    show_b = _extract_between(
        text,
        'show port b/gnss | match "Angle     :"',
        ["logout"],
    )
    match_a = ELEV_RE.search(show_a)
    match_b = ELEV_RE.search(show_b)
    if not match_a:
        raise ValueError("找不到 Elev. Mask Angle（show port a/gnss）")
    if not match_b:
        raise ValueError("找不到 Elev. Mask Angle（show port b/gnss）")
    return {"A": match_a.group(1), "B": match_b.group(1)}


def _pad_signals(values: list[int]) -> list[str]:
    if len(values) > MAX_SIGNALS:
        values = values[:MAX_SIGNALS]
    result = [str(v) for v in values]
    while len(result) < MAX_SIGNALS:
        result.append(SIGNAL_PAD)
    return result


def _constellation_summary(count_a: int, count_b: int) -> str:
    return f"{count_a + count_b}({count_a}+{count_b})"


def parse_gnss_text(
    text: str,
    source_archive: str = "",
    source_txt_path: str = "",
) -> list[GnssRow]:
    hostname = parse_hostname(text)
    begin_time = parse_begin_timestamp(text)
    elev_angles = parse_elev_mask_angles(text)

    dump_a_block = _extract_between(
        text,
        "tools dump port a/gnss gnss",
        ["tools dump port b/gnss gnss"],
    )
    dump_b_block = _extract_between(
        text,
        "tools dump port b/gnss gnss",
        ['show port a/gnss | match "Angle     :"'],
    )
    dump_a = parse_dump_block(dump_a_block)
    dump_b = parse_dump_block(dump_b_block)

    rows: list[GnssRow] = []
    control_labels = {"GPS": "A", "GLONASS": "B"}
    control_totals = {"GPS": str(dump_a.total_used), "GLONASS": str(dump_b.total_used)}

    for constellation in CONSTELLATIONS:
        a_vals = dump_a.signals[constellation]
        b_vals = dump_b.signals[constellation]
        if not a_vals and not b_vals:
            continue
        rows.append(
            GnssRow(
                source_archive=source_archive,
                source_txt_path=source_txt_path,
                hostname=hostname,
                control=control_labels[constellation],
                elev_mask_angle=elev_angles[control_labels[constellation]],
                used_satellite_control=control_totals[constellation],
                constellation=constellation,
                used_satellite_constellation=_constellation_summary(len(a_vals), len(b_vals)),
                a_signals=_pad_signals(a_vals),
                b_signals=_pad_signals(b_vals),
                script_begin_time=begin_time,
            )
        )
    if not rows:
        raise ValueError("未找到 GPS 或 GLONASS 衛星資料")
    return rows
