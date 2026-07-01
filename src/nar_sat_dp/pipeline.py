"""主處理流程。"""

from __future__ import annotations

import sys
from pathlib import Path

from .config import FieldsConfig, PipelineConfig
from .extractors import iter_txt_from_7z, iter_txt_from_zip, read_txt_file
from .parser import parse_text
from .scanner import collect_input_paths
from .writer import ErrorLog, write_csv


def run(
    inputs: list[Path],
    output: Path,
    pipeline: PipelineConfig,
    fields: FieldsConfig,
) -> int:
    paths = collect_input_paths(inputs, pipeline)
    if not paths:
        print("找不到可處理的輸入檔案。", file=sys.stderr)
        return 2

    error_log = ErrorLog(
        output.with_name(output.stem + pipeline.error_log_suffix)
    )
    headers = _build_headers(pipeline, fields)
    rows: list[dict[str, str]] = []
    processed_txt_count = 0
    had_errors = False

    archive_exts = {ext.lower() for ext in pipeline.archive_extensions}

    for path in paths:
        suffix = path.suffix.lower()
        try:
            if suffix == ".txt":
                sources = [read_txt_file(path, pipeline)]
            elif suffix == ".zip":
                sources = iter_txt_from_zip(path, pipeline)
                print(f"已解壓 zip: {path}", file=sys.stderr)
            elif suffix == ".7z":
                sources = iter_txt_from_7z(path, pipeline)
                print(f"已解壓 7z: {path}", file=sys.stderr)
            elif suffix in archive_exts:
                error_log.error(f"不支援的壓縮格式: {path}")
                had_errors = True
                continue
            else:
                continue
        except Exception as exc:
            error_log.error(f"{path}: {exc}")
            had_errors = True
            if not pipeline.continue_on_error:
                break
            continue

        if not sources:
            error_log.warning(f"未找到 .txt: {path}")
            had_errors = True
            continue

        for source in sources:
            try:
                parsed, warnings = parse_text(
                    source.content, fields.fields, pipeline
                )
                row = _build_row(source, parsed, pipeline)
                rows.append(row)
                for w in warnings:
                    error_log.warning(f"{source.source_archive or source.source_txt_path}: {w}")
                    had_errors = True
            except Exception as exc:
                error_log.error(
                    f"{source.source_archive}/{source.source_txt_path}: {exc}"
                )
                had_errors = True
                if not pipeline.continue_on_error:
                    break
                continue

            processed_txt_count += 1
            if (
                pipeline.progress_every_n_files > 0
                and processed_txt_count % pipeline.progress_every_n_files == 0
            ):
                print(f"已處理 {processed_txt_count} 個 txt…", file=sys.stderr)

    if not rows:
        error_log.write()
        print("未產出任何資料列。", file=sys.stderr)
        return 2

    write_csv(
        output,
        headers,
        rows,
        pipeline.output_encoding,
        pipeline.csv_delimiter,
    )
    error_log.info(f"已寫入 {len(rows)} 列至 {output}")
    error_log.write()

    print(f"完成: {output} ({len(rows)} 列)", file=sys.stderr)
    return 1 if had_errors else 0


def _build_headers(pipeline: PipelineConfig, fields: FieldsConfig) -> list[str]:
    headers: list[str] = []
    if pipeline.source_archive:
        headers.append("source_archive")
    if pipeline.source_txt_path:
        headers.append("source_txt_path")
    headers.extend(f.name for f in fields.fields)
    return headers


def _build_row(
    source,
    parsed: dict[str, str],
    pipeline: PipelineConfig,
) -> dict[str, str]:
    row: dict[str, str] = {}
    if pipeline.source_archive:
        row["source_archive"] = source.source_archive
    if pipeline.source_txt_path:
        row["source_txt_path"] = source.source_txt_path
    row.update(parsed)
    return row
