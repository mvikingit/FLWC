from __future__ import annotations

import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from flwc.schemas.common import ValidatorResult, ValidatorStatus
from flwc.validators.candidate_package import validate_candidate_package_file
from flwc.validators.core import aggregate_validator_results


class CandidatePackageValidatorTests(unittest.TestCase):
    def test_valid_synthetic_candidate_package_accepts(self) -> None:
        path = ROOT / "tests" / "fixtures" / "valid" / "synthetic_candidate_package_valid.json"
        summary = validate_candidate_package_file(path)
        self.assertEqual(summary["aggregate_result"], "ACCEPT")
        self.assertEqual(summary["rejected_count"], 0)
        self.assertEqual(summary["accepted_count"], len(summary["validator_results"]))
        self.assertIn("not_truth_authority", summary["non_claims"])
        self.assertIn("not_trade_signal", summary["non_claims"])

    def test_missing_non_claims_rejects(self) -> None:
        path = ROOT / "tests" / "fixtures" / "invalid" / "candidate_missing_non_claims.json"
        summary = validate_candidate_package_file(path)
        self.assertEqual(summary["aggregate_result"], "REJECT")
        reasons = [r["reason_code"] for r in summary["validator_results"]]
        self.assertIn("missing_mandatory_non_claims", reasons)

    def test_invalid_synthetic_fixtures_reject_with_expected_reason(self) -> None:
        cases = {
            "candidate_missing_required_field.json": "required_field_missing",
            "candidate_payload_policy_denial.json": "forbidden_payload_flag_not_false",
            "candidate_non_synthetic_scope.json": "b0_non_synthetic_scope_rejected",
            "candidate_secret_like_value.json": "secret_like_value_detected",
        }
        for filename, expected_reason in cases.items():
            with self.subTest(filename=filename):
                path = ROOT / "tests" / "fixtures" / "invalid" / filename
                summary = validate_candidate_package_file(path)
                self.assertEqual(summary["aggregate_result"], "REJECT")
                reasons = [r["reason_code"] for r in summary["validator_results"]]
                self.assertIn(expected_reason, reasons)
                self.assertEqual(
                    summary["rejected_count"],
                    sum(1 for result in summary["validator_results"] if result["result"] == "REJECT"),
                )

    def test_aggregation_precedence(self) -> None:
        result_sets = (
            (
                (
                    ValidatorResult("a", ValidatorStatus.ACCEPT, "accepted"),
                    ValidatorResult("b", ValidatorStatus.NEUTRALIZE, "neutralized"),
                ),
                ValidatorStatus.NEUTRALIZE,
            ),
            (
                (
                    ValidatorResult("a", ValidatorStatus.NEUTRALIZE, "neutralized"),
                    ValidatorResult("b", ValidatorStatus.HOLD_REVIEW, "hold"),
                ),
                ValidatorStatus.HOLD_REVIEW,
            ),
            (
                (
                    ValidatorResult("a", ValidatorStatus.HOLD_REVIEW, "hold"),
                    ValidatorResult("b", ValidatorStatus.REJECT, "reject"),
                ),
                ValidatorStatus.REJECT,
            ),
        )
        for results, expected in result_sets:
            with self.subTest(expected=expected):
                self.assertEqual(aggregate_validator_results(results), expected)

    def test_validator_output_has_a5_fields_and_bounded_details(self) -> None:
        path = ROOT / "tests" / "fixtures" / "invalid" / "candidate_missing_required_field.json"
        summary = validate_candidate_package_file(path)

        for key in (
            "validator_summary_id",
            "run_id",
            "input_artifact_refs",
            "validator_result_refs",
            "accepted_count",
            "rejected_count",
            "hold_review_count",
            "neutralized_count",
            "producer_id",
            "producer_version",
            "non_claims",
        ):
            self.assertIn(key, summary)

        schema_result = next(
            result for result in summary["validator_results"] if result["validator_id"] == "candidate_package_schema_validator"
        )
        for key in (
            "validator_version",
            "artifact_ref",
            "artifact_schema_version",
            "run_id",
            "run_started_at_ns",
            "run_completed_at_ns",
            "field_refs",
            "input_refs",
            "lineage_digest_checked",
            "non_claims_checked",
            "producer_id",
            "non_claims",
        ):
            self.assertIn(key, schema_result)
        self.assertIn("candidate_package_id", schema_result["field_refs"])
        self.assertLessEqual(len(schema_result["reason_detail_bounded"]), 512)
        self.assertIn("not_runtime_authority", schema_result["non_claims"])


if __name__ == "__main__":
    unittest.main()
