"""GNSS 批次處理主流程。"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

from .config import PipelineConfig
from .extractors import TextSource, iter_txt_from_7z, iter_txt_from_zip, read_txt_file
from .gnss_output import write_gnss_csv, write_gnss_xlsx
from .gnss_parser import GnssRow, parse_gnss_text
from .scanner import collect_input_paths
from .writer import ErrorLog

_ARCHIVE_LABELS = {".zip": "zip", ".7z": "7z"}


@dataclass
class RunResult:
    exit_code: int
    output_csv: Path | None
    output_xlsx: Path | None
    error_log_path: Path | None
    row_count: int
    input_items: int
    txt_succeeded: int
    txt_failed: int


def resolve_output_base(path: Path) -> Path:
    if path.suffix.lower() in {".csv", ".xlsx"}:
        return path.with_suffix("")
    return path


def default_output_base(inputs: list[Path]) -> Path:
    if len(inputs) == 1:
        first = inputs[0].resolve()
        base = first if first.is_dir() else first.parent
    else:
        base = inputs[0].resolve().parent
    return base / "merged"


def run_gnss(
    inputs: list[Path],
    output: Path,
    pipeline: PipelineConfig,
) -> RunResult:
    output_base = resolve_output_base(output)
    csv_path = output_base.with_suffix(".csv")
    xlsx_path = output_base.with_suffix(".xlsx")
    error_log_path = output_base.with_name(output_base.stem + pipeline.error_log_suffix)

    paths = collect_input_paths(inputs, pipeline)
    if not paths:
        print("找不到可處理的輸入檔案（.txt / .zip / .7z）。", file=sys.stderr)
        return RunResult(2, None, None, None, 0, 0, 0, 0)

    error_log = ErrorLog(error_log_path)
    rows: list[GnssRow] = []
    txt_succeeded = 0
    txt_failed = 0
    had_errors = False
    include_source = pipeline.source_archive or pipeline.source_txt_path

    print(f"掃描完成：{len(paths)} 個輸入項目", file=sys.stderr)

    archive_exts = {ext.lower() for ext in pipeline.archive_extensions}

    for index, path in enumerate(paths, start=1):
        print(f"[{index}/{len(paths)}] 處理: {path}", file=sys.stderr)
        suffix = path.suffix.lower()

        try:
            sources = _load_sources(path, pipeline, suffix, archive_exts)
        except Exception as exc:
            error_log.error(f"{path}: {exc}")
            had_errors = True
            txt_failed += 1
            print(f"  ✗ 無法讀取: {exc}", file=sys.stderr)
            if not pipeline.continue_on_error:
                break
            continue

        if not sources:
            error_log.warning(f"未找到 .txt: {path}")
            had_errors = True
            print("  ! 未找到 .txt", file=sys.stderr)
            continue

        if suffix in _ARCHIVE_LABELS:
            print(f"  → {len(sources)} 個 txt", file=sys.stderr)

        for source in sources:
            label = _source_label(source)
            try:
                parsed = parse_gnss_text(
                    source.content,
                    source_archive=source.source_archive,
                    source_txt_path=source.source_txt_path,
                )
                rows.extend(parsed)
                txt_succeeded += 1
                print(f"  ✓ {label} → {len(parsed)} 列", file=sys.stderr)
            except Exception as exc:
                error_log.error(f"{label}: {exc}")
                had_errors = True
                txt_failed += 1
                print(f"  ✗ {label}: {exc}", file=sys.stderr)
                if not pipeline.continue_on_error:
                    break
                continue

            if (
                pipeline.progress_every_n_files > 0
                and txt_succeeded % pipeline.progress_every_n_files == 0
            ):
                print(f"  … 累計已解析 {txt_succeeded} 個 txt", file=sys.stderr)

        if not pipeline.continue_on_error and had_errors:
            break

    if not rows:
        error_log.write()
        print("未產出任何資料列。", file=sys.stderr)
        result = RunResult(
            2, None, None,
            error_log_path if error_log.has_entries else None,
            0, len(paths), txt_succeeded, txt_failed,
        )
        _print_summary(result)
        return result

    write_gnss_csv(csv_path, rows, pipeline.output_encoding, include_source)
    write_gnss_xlsx(xlsx_path, rows, include_source)
    if had_errors:
        error_log.info(f"已寫入 {len(rows)} 列至 {csv_path} / {xlsx_path}")
        error_log.write()

    exit_code = 1 if had_errors else 0
    result = RunResult(
        exit_code=exit_code,
        output_csv=csv_path,
        output_xlsx=xlsx_path,
        error_log_path=error_log_path if error_log.has_entries else None,
        row_count=len(rows),
        input_items=len(paths),
        txt_succeeded=txt_succeeded,
        txt_failed=txt_failed,
    )
    _print_summary(result)
    return result


def _load_sources(
    path: Path,
    pipeline: PipelineConfig,
    suffix: str,
    archive_exts: set[str],
) -> list[TextSource]:
    if suffix == ".txt":
        return [read_txt_file(path, pipeline)]
    if suffix == ".zip":
        print("  解壓 zip…", file=sys.stderr)
        return iter_txt_from_zip(path, pipeline)
    if suffix == ".7z":
        print("  解壓 7z…", file=sys.stderr)
        return iter_txt_from_7z(path, pipeline)
    if suffix in archive_exts:
        raise ValueError(f"不支援的壓縮格式: {suffix}")
    return []


def _source_label(source: TextSource) -> str:
    if source.source_archive:
        return f"{source.source_archive}/{source.source_txt_path}"
    return source.source_txt_path


def _print_summary(result: RunResult) -> None:
    print("", file=sys.stderr)
    print("========== 執行結果 ==========", file=sys.stderr)
    print(f"  輸入項目: {result.input_items}", file=sys.stderr)
    print(f"  成功 txt: {result.txt_succeeded}", file=sys.stderr)
    print(f"  失敗 txt: {result.txt_failed}", file=sys.stderr)
    print(f"  輸出列數: {result.row_count}", file=sys.stderr)
    if result.output_csv:
        print(f"  CSV:      {result.output_csv}", file=sys.stderr)
    if result.output_xlsx:
        print(f"  Excel:    {result.output_xlsx}", file=sys.stderr)
    if result.error_log_path and result.error_log_path.exists():
        print(f"  錯誤 log: {result.error_log_path}", file=sys.stderr)
    if result.exit_code == 0:
        print("  狀態:     成功", file=sys.stderr)
    elif result.exit_code == 1:
        print("  狀態:     完成（有警告或部分失敗）", file=sys.stderr)
    else:
        print("  狀態:     失敗（未產出報表）", file=sys.stderr)
    print("==============================", file=sys.stderr)
