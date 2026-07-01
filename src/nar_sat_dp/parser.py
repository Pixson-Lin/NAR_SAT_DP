"""欄位擷取邏輯。"""

from __future__ import annotations

import re

from .config import FieldRule, PipelineConfig


def extract_field(
    text: str,
    rule: FieldRule,
    pipeline: PipelineConfig,
) -> str | None:
    if rule.type == "label":
        return _extract_label(text, rule, pipeline)
    if rule.type == "regex":
        return _extract_regex(text, rule, pipeline)
    return None


def _extract_label(text: str, rule: FieldRule, pipeline: PipelineConfig) -> str | None:
    if not rule.label:
        return None
    label = rule.label
    flags = re.MULTILINE
    if not pipeline.case_sensitive_labels and not rule.ignore_case:
        flags |= re.IGNORECASE
    if rule.ignore_case:
        flags |= re.IGNORECASE

    for line in text.splitlines():
        stripped = line.strip()
        if rule.ignore_case or not pipeline.case_sensitive_labels:
            if not stripped.lower().startswith(label.lower()):
                continue
            remainder = stripped[len(label) :]
        else:
            if not stripped.startswith(label):
                continue
            remainder = stripped[len(label) :]

        if rule.separator is not None:
            if rule.separator not in remainder:
                continue
            _, _, value = remainder.partition(rule.separator)
        else:
            value = remainder

        value = value.strip() if pipeline.trim_values else value
        return value or None
    return None


def _extract_regex(text: str, rule: FieldRule, pipeline: PipelineConfig) -> str | None:
    if not rule.pattern:
        return None
    flags = re.MULTILINE | re.DOTALL
    if rule.ignore_case:
        flags |= re.IGNORECASE
    match = re.search(rule.pattern, text, flags)
    if not match:
        return None
    value = match.group(1) if match.lastindex else match.group(0)
    if pipeline.trim_values:
        value = value.strip()
    return value or None


def parse_text(
    text: str,
    fields: list[FieldRule],
    pipeline: PipelineConfig,
) -> tuple[dict[str, str], list[str]]:
    """回傳 (欄位值, 警告訊息列表)。"""
    row: dict[str, str] = {}
    warnings: list[str] = []
    for rule in fields:
        value = extract_field(text, rule, pipeline)
        if value is None:
            row[rule.name] = pipeline.missing_field_value
            warnings.append(f"找不到欄位: {rule.name}")
        else:
            row[rule.name] = value
    return row, warnings
