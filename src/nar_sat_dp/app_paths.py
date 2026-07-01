"""執行期路徑解析（開發環境與 PyInstaller frozen exe）。"""

from __future__ import annotations

import sys
from pathlib import Path


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _exe_dir() -> Path:
    return Path(sys.executable).resolve().parent


def _bundled_dir() -> Path | None:
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        return Path(meipass)
    return None


def resolve_pipeline_config_path(user_path: Path | None = None) -> Path:
    """解析 pipeline.json：明確 -c > exe 旁 config > exe 內建 config > 專案 config。"""
    if user_path is not None:
        return user_path.resolve()

    candidates: list[Path] = []
    if getattr(sys, "frozen", False):
        candidates.append(_exe_dir() / "config" / "pipeline.json")
        bundled = _bundled_dir()
        if bundled is not None:
            candidates.append(bundled / "config" / "pipeline.json")
    else:
        candidates.append(_project_root() / "config" / "pipeline.json")

    for path in candidates:
        if path.exists():
            return path
    return candidates[0]
