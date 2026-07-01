"""Write THIRD_PARTY metadata for release packaging."""

from __future__ import annotations

import importlib.metadata
import shutil
import sys
from pathlib import Path

PACKAGES = ("py7zr", "pyinstaller", "openpyxl", "nar-sat-dp")


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: write_release_metadata.py <THIRD_PARTY_dir>", file=sys.stderr)
        return 2

    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)

    lines = ["# Build-time package versions", ""]
    for name in PACKAGES:
        try:
            dist = importlib.metadata.distribution(name)
            lines.append(f"{name}=={dist.version}")
        except importlib.metadata.PackageNotFoundError:
            lines.append(f"{name}==NOT_INSTALLED")

    (out / "BUILD_VERSIONS.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")

    try:
        py7zr_dist = importlib.metadata.distribution("py7zr")
        py7zr_text = (
            "py7zr\n"
            f"Version: {py7zr_dist.version}\n"
            "License: LGPL-2.1-or-later\n"
            "Home: https://github.com/miurahr/py7zr\n"
            "PyPI: https://pypi.org/project/py7zr/\n"
        )
        (out / "py7zr-LICENSE.txt").write_text(py7zr_text, encoding="utf-8")
    except importlib.metadata.PackageNotFoundError:
        pass

    try:
        openpyxl_dist = importlib.metadata.distribution("openpyxl")
        copied = False
        for f in openpyxl_dist.files or []:
            if f.name in ("LICENCE.rst", "LICENSE", "LICENSE.txt"):
                (out / "openpyxl-LICENSE.txt").write_text(f.read_text(), encoding="utf-8")
                copied = True
                break
        if not copied:
            (out / "openpyxl-LICENSE.txt").write_text(
                f"openpyxl {openpyxl_dist.version}\n"
                "License: MIT\n"
                "https://foss.heptapod.net/openpyxl/openpyxl\n",
                encoding="utf-8",
            )
    except Exception as exc:
        (out / "openpyxl-LICENSE.txt").write_text(
            f"openpyxl license copy failed: {exc}\n", encoding="utf-8"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
