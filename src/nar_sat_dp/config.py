"""設定檔載入。"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class PipelineConfig:
    txt_glob: str = "*.txt"
    archive_extensions: list[str] = field(default_factory=lambda: [".zip", ".7z"])
    recursive_scan: bool = True
    source_archive: bool = True
    source_txt_path: bool = True
    input_encodings: list[str] = field(
        default_factory=lambda: ["utf-8-sig", "utf-8", "cp950"]
    )
    output_encoding: str = "utf-8-sig"
    csv_delimiter: str = ","
    missing_field_value: str = ""
    continue_on_error: bool = True
    error_log_suffix: str = "_errors.log"
    progress_every_n_files: int = 50
    seven_zip_enabled: bool = True
    trim_values: bool = True
    case_sensitive_labels: bool = True


@dataclass
class FieldRule:
    name: str
    type: str
    label: str | None = None
    separator: str | None = None
    pattern: str | None = None
    ignore_case: bool = False


@dataclass
class FieldsConfig:
    fields: list[FieldRule]


def _load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def load_pipeline_config(path: Path) -> PipelineConfig:
    data = _load_json(path)
    enc = data.get("encoding", {})
    csv_cfg = data.get("csv", {})
    err = data.get("error_handling", {})
    src = data.get("source_columns", {})
    match = data.get("matching_defaults", {})
    seven = data.get("seven_zip", {})
    return PipelineConfig(
        txt_glob=data.get("txt_glob", "*.txt"),
        archive_extensions=data.get("archive_extensions", [".zip", ".7z"]),
        recursive_scan=data.get("recursive_scan", True),
        source_archive=src.get("source_archive", True),
        source_txt_path=src.get("source_txt_path", True),
        input_encodings=enc.get("input_fallback_order", ["utf-8-sig", "utf-8", "cp950"]),
        output_encoding=enc.get("output", "utf-8-sig"),
        csv_delimiter=csv_cfg.get("delimiter", ","),
        missing_field_value=csv_cfg.get("missing_field_value", ""),
        continue_on_error=err.get("continue_on_error", True),
        error_log_suffix=err.get("error_log_suffix", "_errors.log"),
        progress_every_n_files=err.get("progress_every_n_files", 50),
        seven_zip_enabled=seven.get("enabled", True),
        trim_values=match.get("trim_values", True),
        case_sensitive_labels=match.get("case_sensitive_labels", True),
    )


def load_fields_config(path: Path) -> FieldsConfig:
    data = _load_json(path)
    fields = [
        FieldRule(
            name=item["name"],
            type=item["type"],
            label=item.get("label"),
            separator=item.get("separator"),
            pattern=item.get("pattern"),
            ignore_case=item.get("ignore_case", False),
        )
        for item in data.get("fields", [])
    ]
    return FieldsConfig(fields=fields)
