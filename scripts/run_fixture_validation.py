#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from flwc.validators.candidate_package import validate_candidate_package_file


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: run_fixture_validation.py <candidate_package.json>", file=sys.stderr)
        return 2
    summary = validate_candidate_package_file(argv[1])
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if summary["aggregate_result"] == "ACCEPT" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
