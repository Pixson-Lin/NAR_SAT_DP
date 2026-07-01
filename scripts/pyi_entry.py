"""PyInstaller entry point (absolute imports; do not use package __main__)."""

from __future__ import annotations

import sys

from nar_sat_dp.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
