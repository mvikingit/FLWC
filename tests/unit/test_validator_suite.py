from __future__ import annotations

from copy import deepcopy
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from flwc.compiler.validator_suite_fixtures import (
    build_claim_event_reject_validator_suite_packet,
    build_hold_review_validator_suite_packet,
    build_raw_evidence_reject_validator_suite_packet,
    build_source_license_reject_validator_suite_packet,
    build_valid_validator_suite_packet,
)
from flwc.schemas.common import ValidatorResult, ValidatorStatus
from flwc.schemas.validator_suite import (
    FLWCRefusalRecordV1,
    PrimaryRefusalFamily,
    ReviewStatus,
    ValidatorFamily,
    ValidatorScope,
)
from flwc.validators.core import aggregate_validator_results
from flwc.validators.validator_suite import build_refusal_record_from_results, validate_fixture_suite_packet


class ValidatorSuiteTests(unittest.TestCase):
    def test_a5_enums_and_refusal_record_round_trip(self) -> None:
        self.assertEqual(ValidatorFamily("raw_llm_output_denial"), ValidatorFamily.RAW_LLM_OUTPUT_DENIAL)
        self.assertEqual(ValidatorScope("synthetic_fixture"), ValidatorScope.SYNTHETIC_FIXTURE)
        self.assertEqual(PrimaryRefusalFamily("missing_non_claims"), PrimaryRefusalFamily.MISSING_NON_CLAIMS)
        self.assertEqual(ReviewStatus("rejected_final"), ReviewStatus.REJECTED_FINAL)

        record = build_refusal_record_from_results(
            [ValidatorResult("non_claims_validator", ValidatorStatus.REJECT, "missing_mandatory_non_claims")]
        )
        parsed, issues = FLWCRefusalRecordV1.from_mapping(record.as_dict())
        self.assertEqual(issues, ())
        self.assertEqual(parsed.as_dict(), record.as_dict())

    def test_valid_full_chain_suite_accepts(self) -> None:
        summary = validate_fixture_suite_packet(build_valid_validator_suite_packet())
        self.assertEqual(summary["aggregate_result"], "ACCEPT")
        self.assertEqual(summary["rejected_count"], 0)
        self.assertEqual(summary["hold_review_count"], 0)
        self.assertEqual(summary["neutralized_count"], 0)
        self.assertEqual(summary["refusal_record_refs"], [])
        self.assertEqual(summary["refusal_records"], [])
        self.assertEqual(len(summary["component_summaries"]), 3)
        self.assertIn("not_canonical_snapshot", summary["non_claims"])

    def test_source_license_raw_evidence_and_claim_event_rejects_emit_refusal_records(self) -> None:
        cases = (
            (
                build_source_license_reject_validator_suite_packet,
                "source_license_pair_not_accepted",
                PrimaryRefusalFamily.SOURCE_LICENSE_MISMATCH.value,
            ),
            (
                build_raw_evidence_reject_validator_suite_packet,
                "raw_text_payload_field_present",
                PrimaryRefusalFamily.RAW_TEXT_DENIAL.value,
            ),
            (
                build_claim_event_reject_validator_suite_packet,
                "raw_text_payload_field_present",
                PrimaryRefusalFamily.RAW_LLM_OUTPUT_DENIAL.value,
            ),
        )
        for builder, expected_reason, expected_family in cases:
            with self.subTest(builder=builder.__name__):
                summary = validate_fixture_suite_packet(builder())
                self.assertEqual(summary["aggregate_result"], "REJECT")
                self.assertIn(expected_reason, _reason_codes(summary))
                self.assertEqual(len(summary["refusal_records"]), 1)
                refusal = summary["refusal_records"][0]
                self.assertEqual(refusal["aggregate_result"], "REJECT")
                self.assertEqual(refusal["review_status"], ReviewStatus.REJECTED_FINAL.value)
                self.assertEqual(refusal["primary_refusal_family"], expected_family)
                self.assertTrue(refusal["validator_result_refs"])
                self.assertIn(expected_reason, refusal["reason_codes"])

    def test_hold_review_suite_emits_hold_refusal_record(self) -> None:
        summary = validate_fixture_suite_packet(build_hold_review_validator_suite_packet())
        self.assertEqual(summary["aggregate_result"], "HOLD_REVIEW")
        self.assertIn("source_policy_value_unrecognized_requires_review", _reason_codes(summary))
        self.assertEqual(len(summary["refusal_records"]), 1)
        refusal = summary["refusal_records"][0]
        self.assertEqual(refusal["aggregate_result"], "HOLD_REVIEW")
        self.assertEqual(refusal["review_status"], ReviewStatus.HOLD_REVIEW.value)

    def test_boundary_payloads_and_missing_non_claims_reject_through_suite(self) -> None:
        packet = build_valid_validator_suite_packet()
        packet["atomic_claim"]["model_output"] = "synthetic model output denied"
        summary = validate_fixture_suite_packet(packet)
        self.assertEqual(summary["aggregate_result"], "REJECT")
        self.assertIn("raw_text_payload_field_present", _reason_codes(summary))
        self.assertEqual(summary["refusal_records"][0]["primary_refusal_family"], PrimaryRefusalFamily.RAW_LLM_OUTPUT_DENIAL.value)

        packet = build_valid_validator_suite_packet()
        packet["raw_evidence_record"]["raw_text"] = "synthetic raw text denied"
        summary = validate_fixture_suite_packet(packet)
        self.assertEqual(summary["aggregate_result"], "REJECT")
        self.assertIn("raw_text_payload_field_present", _reason_codes(summary))

        forbidden_fields = (
            ("financial_event", "future_outcome", "future_outcome_field_present"),
            ("financial_event", "trade_signal", "trade_signal_field_present"),
            ("financial_event", "order_intent", "order_intent_field_present"),
            ("financial_event", "position_target", "position_target_field_present"),
            ("financial_event", "execution_instruction", "broker_execution_field_present"),
        )
        for artifact, field, reason in forbidden_fields:
            with self.subTest(field=field):
                packet = build_valid_validator_suite_packet()
                packet[artifact][field] = "synthetic forbidden boundary field"
                summary = validate_fixture_suite_packet(packet)
                self.assertEqual(summary["aggregate_result"], "REJECT")
                self.assertIn(reason, _reason_codes(summary))

        packet = build_valid_validator_suite_packet()
        packet["atomic_claim"]["non_claims"] = ["synthetic_fixture_only"]
        summary = validate_fixture_suite_packet(packet)
        self.assertEqual(summary["aggregate_result"], "REJECT")
        self.assertIn("missing_mandatory_non_claims", _reason_codes(summary))
        self.assertEqual(summary["refusal_records"][0]["primary_refusal_family"], PrimaryRefusalFamily.MISSING_NON_CLAIMS.value)

    def test_summary_counts_and_precedence_are_deterministic(self) -> None:
        first = validate_fixture_suite_packet(build_valid_validator_suite_packet())
        second = validate_fixture_suite_packet(build_valid_validator_suite_packet())
        self.assertEqual(first, second)
        self.assertEqual(first["accepted_count"], len(first["validator_results"]))

        results = (
            ValidatorResult("accept", ValidatorStatus.ACCEPT, "accepted"),
            ValidatorResult("neutral", ValidatorStatus.NEUTRALIZE, "neutralized"),
            ValidatorResult("hold", ValidatorStatus.HOLD_REVIEW, "hold"),
            ValidatorResult("reject", ValidatorStatus.REJECT, "reject"),
        )
        self.assertEqual(aggregate_validator_results(results), ValidatorStatus.REJECT)
        refusal = build_refusal_record_from_results(results)
        self.assertEqual(refusal.aggregate_result, ValidatorStatus.REJECT)
        self.assertEqual(refusal.review_status, ReviewStatus.REJECTED_FINAL)

    def test_no_silent_repair_and_input_immutability(self) -> None:
        packet = build_valid_validator_suite_packet()
        packet["source_manifest"]["revision_policy"] = "custom_review_policy"
        before = deepcopy(packet)
        summary = validate_fixture_suite_packet(packet)
        self.assertEqual(summary["aggregate_result"], "HOLD_REVIEW")
        self.assertEqual(packet, before)

    def test_missing_suite_artifact_rejects_without_payload_echo(self) -> None:
        packet = build_valid_validator_suite_packet()
        del packet["financial_event"]
        summary = validate_fixture_suite_packet(packet)
        self.assertEqual(summary["aggregate_result"], "REJECT")
        self.assertIn("required_field_missing", _reason_codes(summary))
        refusal = summary["refusal_records"][0]
        self.assertEqual(refusal["primary_refusal_family"], PrimaryRefusalFamily.SCHEMA_INVALID.value)
        self.assertNotIn("synthetic model output denied", str(refusal))


def _reason_codes(summary: dict[str, object]) -> set[str]:
    return {str(result["reason_code"]) for result in summary["validator_results"]}


if __name__ == "__main__":
    unittest.main()
