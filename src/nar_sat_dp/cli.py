"""命令列介面與拖放支援。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .app_paths import resolve_pipeline_config_path
from .config import load_pipeline_config
from .gnss_pipeline import default_output_base, run_gnss


def build_parser() -> argparse.ArgumentParser:
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
        default=None,
        help="pipeline 設定檔（預設：exe 旁 config/，否則使用內建）",
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

    config_path = resolve_pipeline_config_path(args.config)
    if not config_path.exists():
        print(f"找不到設定檔: {config_path}", file=sys.stderr)
        _pause_if_frozen()
        return 2

    input_paths = [Path(p) for p in args.inputs]
    output = args.output if args.output is not None else default_output_base(input_paths)
    pipeline = load_pipeline_config(config_path)
    result = run_gnss(input_paths, output.resolve(), pipeline)
    _pause_if_frozen()
    return result.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
