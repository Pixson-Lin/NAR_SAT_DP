"""壓縮檔與文字檔讀取。"""

from __future__ import annotations

import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from .config import PipelineConfig
from .encoding_util import decode_bytes


@dataclass
class TextSource:
    content: str
    source_archive: str
    source_txt_path: str
    encoding: str


def read_txt_file(path: Path, pipeline: PipelineConfig) -> TextSource:
    data = path.read_bytes()
    text, encoding = decode_bytes(data, pipeline.input_encodings)
    return TextSource(
        content=text,
        source_archive="",
        source_txt_path=_normalize_path(path),
        encoding=encoding,
    )


def iter_txt_from_zip(
    archive_path: Path,
    pipeline: PipelineConfig,
) -> list[TextSource]:
    sources: list[TextSource] = []
    archive_name = _normalize_path(archive_path)
    with zipfile.ZipFile(archive_path, "r") as zf:
        for info in zf.infolist():
            if info.is_dir():
                continue
            name = PurePosixPath(info.filename)
            if name.suffix.lower() != ".txt":
                continue
            data = zf.read(info)
            text, encoding = decode_bytes(data, pipeline.input_encodings)
            sources.append(
                TextSource(
                    content=text,
                    source_archive=archive_name,
                    source_txt_path=str(name).replace("\\", "/"),
                    encoding=encoding,
                )
            )
    return sources


def iter_txt_from_7z(
    archive_path: Path,
    pipeline: PipelineConfig,
) -> list[TextSource]:
    if not pipeline.seven_zip_enabled:
        raise RuntimeError("7z 支援未啟用（pipeline.seven_zip.enabled=false）")
    try:
        import py7zr
    except ImportError as exc:
        raise RuntimeError(
            "需要 py7zr 才能讀取 .7z（開發/打包用；exe 會內嵌）"
        ) from exc

    sources: list[TextSource] = []
    archive_name = _normalize_path(archive_path)
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        with py7zr.SevenZipFile(archive_path, mode="r") as archive:
            archive.extractall(path=tmp_path)
        for txt_path in sorted(tmp_path.rglob("*.txt")):
            rel = txt_path.relative_to(tmp_path).as_posix()
            data = txt_path.read_bytes()
            text, encoding = decode_bytes(data, pipeline.input_encodings)
            sources.append(
                TextSource(
                    content=text,
                    source_archive=archive_name,
                    source_txt_path=rel,
                    encoding=encoding,
                )
            )
    return sources


def _normalize_path(path: Path) -> str:
    try:
        rel = path.resolve().relative_to(Path.cwd())
    except ValueError:
        rel = path.resolve()
    return rel.as_posix()
