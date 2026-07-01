"""解析單一或多個 GNSS log，輸出 CSV + Excel 供規則確認。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from nar_sat_dp.encoding_util import decode_bytes
from nar_sat_dp.gnss_output import write_gnss_csv, write_gnss_xlsx
from nar_sat_dp.gnss_parser import parse_gnss_text

ENCODINGS = ["utf-8-sig", "utf-8", "cp950"]


def read_text(path: Path) -> str:
    data = path.read_bytes()
    text, _ = decode_bytes(data, ENCODINGS)
    return text


def main() -> int:
    parser = argparse.ArgumentParser(description="GNSS log 解析預覽（CSV + Excel）")
    parser.add_argument("inputs", nargs="+", type=Path, help="輸入 .txt 路徑")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        required=True,
        help="輸出路徑（不含副檔名，會產出 .csv 與 .xlsx）",
    )
    args = parser.parse_args()

    all_rows = []
    for path in args.inputs:
        text = read_text(path.resolve())
        rel = path.resolve()
        try:
            rel = rel.relative_to(Path.cwd())
        except ValueError:
            pass
        rows = parse_gnss_text(text, source_txt_path=rel.as_posix())
        all_rows.extend(rows)

    base = args.output
    if base.suffix.lower() in {".csv", ".xlsx"}:
        base = base.with_suffix("")

    csv_path = Path(f"{base}.csv")
    xlsx_path = Path(f"{base}.xlsx")
    write_gnss_csv(csv_path, all_rows, include_source=bool(all_rows and all_rows[0].source_txt_path))
    write_gnss_xlsx(xlsx_path, all_rows, include_source=bool(all_rows and all_rows[0].source_txt_path))

    print(f"CSV:   {csv_path}")
    print(f"Excel: {xlsx_path}")
    print(f"共 {len(all_rows)} 列")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
