"""命令列介面與拖放支援。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .config import load_fields_config, load_pipeline_config
from .pipeline import run


def _default_config_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent / "config"
    return Path(__file__).resolve().parents[2] / "config"


def build_parser() -> argparse.ArgumentParser:
    cfg = _default_config_dir()
    parser = argparse.ArgumentParser(
        prog="nar_sat_dp",
        description="批次解析 .txt / .zip / .7z 並合併為 CSV。",
    )
    parser.add_argument(
        "inputs",
        nargs="*",
        help="輸入檔案或資料夾路徑（可拖放到 exe）",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="輸出 CSV 路徑（拖放模式預設為 merged.csv）",
    )
    parser.add_argument(
        "-c",
        "--config",
        type=Path,
        default=cfg / "pipeline.json",
        help="pipeline 設定檔",
    )
    parser.add_argument(
        "-f",
        "--fields",
        type=Path,
        default=cfg / "fields.json",
        help="欄位擷取規則",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.inputs:
        parser.print_help()
        return 2

    output = args.output
    if output is None:
        if len(args.inputs) == 1:
            first = Path(args.inputs[0]).resolve()
            base = first if first.is_dir() else first.parent
        else:
            base = Path(args.inputs[0]).resolve().parent
        output = base / "merged.csv"

    if not args.config.exists():
        print(f"找不到設定檔: {args.config}", file=sys.stderr)
        return 2
    if not args.fields.exists():
        print(f"找不到欄位規則: {args.fields}", file=sys.stderr)
        return 2

    pipeline = load_pipeline_config(args.config)
    fields = load_fields_config(args.fields)
    input_paths = [Path(p) for p in args.inputs]
    return run(input_paths, output.resolve(), pipeline, fields)


if __name__ == "__main__":
    raise SystemExit(main())
