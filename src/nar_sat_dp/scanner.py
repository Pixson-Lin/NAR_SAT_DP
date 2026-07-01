"""輸入路徑掃描。"""

from __future__ import annotations

from pathlib import Path

from .config import PipelineConfig


def collect_input_paths(inputs: list[Path], pipeline: PipelineConfig) -> list[Path]:
    """收集待處理的檔案路徑（txt、zip、7z）。"""
    results: list[Path] = []
    seen: set[Path] = set()
    archive_exts = {ext.lower() for ext in pipeline.archive_extensions}

    for raw in inputs:
        path = raw.resolve()
        if not path.exists():
            continue
        if path.is_file():
            _add_unique(path, results, seen)
            continue
        if path.is_dir():
            _scan_directory(path, pipeline, archive_exts, results, seen)
    return results


def _scan_directory(
    root: Path,
    pipeline: PipelineConfig,
    archive_exts: set[str],
    results: list[Path],
    seen: set[Path],
) -> None:
    iterator = root.rglob("*") if pipeline.recursive_scan else root.glob("*")
    for item in iterator:
        if not item.is_file():
            continue
        suffix = item.suffix.lower()
        if suffix == ".txt" or suffix in archive_exts:
            _add_unique(item.resolve(), results, seen)


def _add_unique(path: Path, results: list[Path], seen: set[Path]) -> None:
    if path not in seen:
        seen.add(path)
        results.append(path)
