from __future__ import annotations

import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from flwc.validators.candidate_package import validate_candidate_package_file


class CandidatePackageValidatorTests(unittest.TestCase):
    def test_valid_synthetic_candidate_package_accepts(self) -> None:
        path = ROOT / "tests" / "fixtures" / "valid" / "synthetic_candidate_package_valid.json"
        summary = validate_candidate_package_file(path)
        self.assertEqual(summary["aggregate_result"], "ACCEPT")

    def test_missing_non_claims_rejects(self) -> None:
        path = ROOT / "tests" / "fixtures" / "invalid" / "candidate_missing_non_claims.json"
        summary = validate_candidate_package_file(path)
        self.assertEqual(summary["aggregate_result"], "REJECT")
        reasons = [r["reason_code"] for r in summary["validator_results"]]
        self.assertIn("missing_mandatory_non_claims", reasons)


if __name__ == "__main__":
    unittest.main()
