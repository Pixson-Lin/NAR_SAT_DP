"""解析 GNSS log 並輸出 CSV + Excel（委派至主流程）。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from nar_sat_dp.config import load_pipeline_config
from nar_sat_dp.gnss_pipeline import default_output_base, run_gnss


def main() -> int:
    parser = argparse.ArgumentParser(description="GNSS log 解析預覽（CSV + Excel）")
    parser.add_argument(
        "inputs",
        nargs="+",
        type=Path,
        help="輸入 .txt / .zip / .7z 或資料夾",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="輸出基底路徑（預設 merged）",
    )
    parser.add_argument(
        "-c",
        "--config",
        type=Path,
        default=ROOT / "config" / "pipeline.json",
        help="pipeline 設定檔",
    )
    args = parser.parse_args()

    inputs = [p.resolve() for p in args.inputs]
    output = args.output.resolve() if args.output else default_output_base(inputs).resolve()
    pipeline = load_pipeline_config(args.config)
    return run_gnss(inputs, output, pipeline).exit_code


if __name__ == "__main__":
    raise SystemExit(main())
