"""建立 samples/archives 下的 zip 與 7z 範例壓縮檔。"""

from __future__ import annotations

import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "scripts" / "sample_sources"
ARCHIVES = ROOT / "samples" / "archives"


def create_zip() -> Path:
    out = ARCHIVES / "sample_batch.zip"
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.write(SOURCES / "batch" / "a.txt", "batch/a.txt")
        zf.write(SOURCES / "batch" / "b.txt", "batch/b.txt")
    return out


def create_7z() -> Path:
    try:
        import py7zr
    except ImportError as exc:
        raise SystemExit("請先安裝 py7zr: pip install py7zr") from exc

    out = ARCHIVES / "sample_batch.7z"
    with py7zr.SevenZipFile(out, "w") as archive:
        archive.write(SOURCES / "7z" / "c.txt", "7z/c.txt")
    return out


def main() -> None:
    ARCHIVES.mkdir(parents=True, exist_ok=True)
    zip_path = create_zip()
    print(f"已建立 {zip_path}")
    seven_path = create_7z()
    print(f"已建立 {seven_path}")


if __name__ == "__main__":
    main()
