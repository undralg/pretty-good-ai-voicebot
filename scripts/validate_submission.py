from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

from pgai_voicebot.validation import validate_project


def main() -> int:
    report = validate_project(PROJECT_ROOT)
    for warning in report.warnings:
        print(f"WARNING: {warning}")
    for error in report.errors:
        print(f"ERROR: {error}")
    print("Submission structure is valid." if report.ok else "Validation failed.")
    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
