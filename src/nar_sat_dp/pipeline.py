"""主處理流程（GNSS）。"""

from __future__ import annotations

from pathlib import Path

from .config import PipelineConfig
from .gnss_pipeline import RunResult, default_output_base, resolve_output_base, run_gnss

__all__ = [
    "RunResult",
    "default_output_base",
    "resolve_output_base",
    "run",
    "run_gnss",
]


def run(
    inputs: list[Path],
    output: Path,
    pipeline: PipelineConfig,
) -> int:
    return run_gnss(inputs, output, pipeline).exit_code
