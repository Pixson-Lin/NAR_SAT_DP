"""命令列介面與拖放支援。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .config import load_pipeline_config
from .gnss_pipeline import default_output_base, run_gnss


def _default_config_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent / "config"
    return Path(__file__).resolve().parents[2] / "config"


def build_parser() -> argparse.ArgumentParser:
    cfg = _default_config_dir()
    parser = argparse.ArgumentParser(
        prog="nar_sat_dp",
        description="批次解析 GNSS 設備 log（.txt / .zip / .7z），合併輸出 CSV + Excel。",
    )
    parser.add_argument(
        "inputs",
        nargs="*",
        help="輸入檔案或資料夾（可拖放到 exe）",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="輸出基底路徑（產出 .csv 與 .xlsx；預設為 merged）",
    )
    parser.add_argument(
        "-c",
        "--config",
        type=Path,
        default=cfg / "pipeline.json",
        help="pipeline 設定檔",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def _pause_if_frozen() -> None:
    if getattr(sys, "frozen", False):
        try:
            input("按 Enter 結束…")
        except EOFError:
            pass


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.inputs:
        parser.print_help()
        print(
            "\n用法：將 .txt、.zip、.7z 或資料夾拖放到 nar_sat_dp.exe 上，"
            "或在命令列指定路徑。",
            file=sys.stderr,
        )
        _pause_if_frozen()
        return 2

    if not args.config.exists():
        print(f"找不到設定檔: {args.config}", file=sys.stderr)
        _pause_if_frozen()
        return 2

    input_paths = [Path(p) for p in args.inputs]
    output = args.output if args.output is not None else default_output_base(input_paths)
    pipeline = load_pipeline_config(args.config)
    result = run_gnss(input_paths, output.resolve(), pipeline)
    _pause_if_frozen()
    return result.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
