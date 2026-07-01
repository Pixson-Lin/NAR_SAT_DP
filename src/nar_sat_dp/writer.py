"""CSV 與錯誤 log 輸出。"""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class ErrorLog:
    path: Path
    _lines: list[str] = field(default_factory=list)

    def error(self, message: str) -> None:
        self._lines.append(f"[ERROR] {message}")

    def warning(self, message: str) -> None:
        self._lines.append(f"[WARN]  {message}")

    def info(self, message: str) -> None:
        self._lines.append(f"[INFO]  {message}")

    def write(self) -> None:
        if not self._lines:
            return
        header = (
            f"# NAR_SAT_DP error log — {datetime.now(timezone.utc).isoformat()}\n"
        )
        self.path.write_text(header + "\n".join(self._lines) + "\n", encoding="utf-8")


def write_csv(
    output_path: Path,
    headers: list[str],
    rows: list[dict[str, str]],
    encoding: str,
    delimiter: str,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding=encoding, newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=headers,
            delimiter=delimiter,
            quoting=csv.QUOTE_MINIMAL,
        )
        writer.writeheader()
        for row in rows:
            writer.writerow({h: row.get(h, "") for h in headers})
