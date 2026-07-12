from __future__ import annotations

from copy import deepcopy
import json
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from flwc.compiler.claim_event_fixtures import (
    build_valid_atomic_claim,
    build_valid_atomic_claim_ledger,
    build_valid_claim_event_compiler_output,
    build_valid_claim_event_pair,
    build_valid_financial_event,
    build_valid_financial_event_table,
)
from flwc.schemas.claim_event import (
    ClaimExtractionMethod,
    ClaimStatus,
    ClaimType,
    EventDerivationMethod,
    EventDirectionCandidate,
    FLWCAtomicClaimLedgerV1,
    FLWCAtomicClaimV1,
    FLWCFinancialEventTableV1,
    FLWCFinancialEventV1,
    FinancialEventStatus,
    FinancialEventType,
)
from flwc.schemas.common import ValidatorResult, ValidatorStatus
from flwc.validators.claim_event import (
    validate_atomic_claim,
    validate_atomic_claim_file,
    validate_atomic_claim_ledger_file,
    validate_claim_event_compiler_output,
    validate_claim_event_compiler_output_file,
    validate_claim_event_pair,
    validate_claim_event_pair_file,
    validate_financial_event,
    validate_financial_event_file,
    validate_financial_event_table_file,
)
from flwc.validators.core import aggregate_validator_results


class ClaimEventValidatorTests(unittest.TestCase):
    def test_exact_a3_enum_acceptance_and_rejection(self) -> None:
        self.assertEqual(ClaimType("guidance_statement"), ClaimType.GUIDANCE_STATEMENT)
        self.assertEqual(ClaimExtractionMethod("manual_fixture"), ClaimExtractionMethod.MANUAL_FIXTURE)
        self.assertEqual(ClaimStatus("proposed"), ClaimStatus.PROPOSED)
        self.assertEqual(FinancialEventType("guidance_update"), FinancialEventType.GUIDANCE_UPDATE)
        self.assertEqual(EventDirectionCandidate("not_applicable"), EventDirectionCandidate.NOT_APPLICABLE)
        self.assertEqual(FinancialEventStatus("proposed"), FinancialEventStatus.PROPOSED)
        self.assertEqual(EventDerivationMethod("claim_set_compiler"), EventDerivationMethod.CLAIM_SET_COMPILER)
        with self.assertRaises(ValueError):
            ClaimType("price_target")
        with self.assertRaises(ValueError):
            ClaimExtractionMethod("llm_runtime")
        with self.assertRaises(ValueError):
            FinancialEventType("trade_signal")
        with self.assertRaises(ValueError):
            EventDerivationMethod("model_extraction_authorized")

    def test_deterministic_builder_and_schema_round_trip(self) -> None:
        first_output = build_valid_claim_event_compiler_output()
        second_output = build_valid_claim_event_compiler_output()
        self.assertEqual(first_output, second_output)

        parsed_ledger, ledger_issues = FLWCAtomicClaimLedgerV1.from_mapping(first_output["atomic_claim_ledger"])
        parsed_claim, claim_issues = FLWCAtomicClaimV1.from_mapping(first_output["atomic_claim"])
        parsed_table, table_issues = FLWCFinancialEventTableV1.from_mapping(first_output["financial_event_table"])
        parsed_event, event_issues = FLWCFinancialEventV1.from_mapping(first_output["financial_event"])
        self.assertEqual(ledger_issues, ())
        self.assertEqual(claim_issues, ())
        self.assertEqual(table_issues, ())
        self.assertEqual(event_issues, ())
        self.assertEqual(parsed_ledger.as_dict(), first_output["atomic_claim_ledger"])
        self.assertEqual(parsed_claim.as_dict(), first_output["atomic_claim"])
        self.assertEqual(parsed_table.as_dict(), first_output["financial_event_table"])
        self.assertEqual(parsed_event.as_dict(), first_output["financial_event"])

    def test_valid_claim_event_fixtures_accept(self) -> None:
        self.assertEqual(
            validate_atomic_claim_ledger_file(ROOT / "tests" / "fixtures" / "valid" / "atomic_claim_ledger_valid.json")[
                "aggregate_result"
            ],
            "ACCEPT",
        )
        self.assertEqual(
            validate_atomic_claim_file(ROOT / "tests" / "fixtures" / "valid" / "atomic_claim_valid.json")["aggregate_result"],
            "ACCEPT",
        )
        self.assertEqual(
            validate_financial_event_table_file(ROOT / "tests" / "fixtures" / "valid" / "financial_event_table_valid.json")[
                "aggregate_result"
            ],
            "ACCEPT",
        )
        self.assertEqual(
            validate_financial_event_file(ROOT / "tests" / "fixtures" / "valid" / "financial_event_valid.json")[
                "aggregate_result"
            ],
            "ACCEPT",
        )
        self.assertEqual(
            validate_claim_event_pair_file(ROOT / "tests" / "fixtures" / "valid" / "claim_event_pair_valid.json")[
                "aggregate_result"
            ],
            "ACCEPT",
        )
        self.assertEqual(
            validate_claim_event_compiler_output_file(
                ROOT / "tests" / "fixtures" / "valid" / "claim_event_compiler_output_valid.json"
            )["aggregate_result"],
            "ACCEPT",
        )

    def test_invalid_fixture_catalog_rejects_or_holds_with_expected_reason(self) -> None:
        cases = _load_json(ROOT / "tests" / "fixtures" / "invalid" / "claim_event_invalid_cases.json")
        for case in cases:
            with self.subTest(case_id=case["case_id"]):
                output = build_valid_claim_event_compiler_output()
                _apply_mutations(output, case)
                summary = _validate_target(case["target"], output)
                self.assertEqual(summary["aggregate_result"], case["expected_result"])
                self.assertIn(case["expected_reason_code"], _reason_codes(summary))

    def test_source_license_raw_evidence_and_claim_event_ref_enforcement(self) -> None:
        output = build_valid_claim_event_compiler_output()
        output["atomic_claim"]["source_manifest_ref"] = "synthetic_source_manifest_mismatch"
        summary = _validate_compiler_output(output)
        self.assertEqual(summary["aggregate_result"], "REJECT")
        self.assertIn("claim_event_ref_mismatch", _reason_codes(summary))

        output = build_valid_claim_event_compiler_output()
        output["license_manifest"]["source_id"] = "synthetic_source_mismatch"
        summary = _validate_compiler_output(output)
        self.assertEqual(summary["aggregate_result"], "REJECT")
        self.assertIn("raw_evidence_pair_not_accepted", _reason_codes(summary))

        output = build_valid_claim_event_compiler_output()
        output["atomic_claim"]["raw_evidence_refs"] = ["synthetic_raw_evidence_mismatch"]
        summary = _validate_compiler_output(output)
        self.assertEqual(summary["aggregate_result"], "REJECT")
        self.assertIn("claim_event_ref_mismatch", _reason_codes(summary))

        pair = build_valid_claim_event_pair()
        pair["financial_event"]["evidence_claim_refs"] = ["synthetic_claim_mismatch"]
        summary = validate_claim_event_pair(pair["atomic_claim"], pair["financial_event"])
        self.assertEqual(summary["aggregate_result"], "REJECT")
        self.assertIn("claim_event_ref_mismatch", _reason_codes(summary))

    def test_source_span_timestamp_and_lineage_fail_closed(self) -> None:
        claim = build_valid_atomic_claim(source_span_refs=["synthetic_doc_001#segment:1"])
        summary = validate_atomic_claim(claim)
        self.assertEqual(summary["aggregate_result"], "REJECT")
        self.assertIn("source_span_ref_invalid", _reason_codes(summary))

        output = build_valid_claim_event_compiler_output()
        output["atomic_claim"]["source_span_refs"] = ["synthetic_doc_001#segment:000002"]
        summary = _validate_compiler_output(output)
        self.assertEqual(summary["aggregate_result"], "REJECT")
        self.assertIn("source_document_segment_ref_invalid", _reason_codes(summary))

        claim = build_valid_atomic_claim(source_timestamp_ns=None)
        summary = validate_atomic_claim(claim)
        self.assertEqual(summary["aggregate_result"], "REJECT")
        self.assertIn("source_timestamp_missing", _reason_codes(summary))

        event = build_valid_financial_event(event_time_ns=1760000000000000999)
        summary = validate_financial_event(event)
        self.assertEqual(summary["aggregate_result"], "REJECT")
        self.assertIn("future_outcome_field_present", _reason_codes(summary))

        claim = build_valid_atomic_claim(lineage_digest="")
        summary = validate_atomic_claim(claim)
        self.assertEqual(summary["aggregate_result"], "REJECT")
        self.assertIn("lineage_digest_missing", _reason_codes(summary))

    def test_boundary_payload_credential_prompt_and_non_claim_enforcement(self) -> None:
        claim = build_valid_atomic_claim(model_output="model text")
        summary = validate_atomic_claim(claim)
        self.assertEqual(summary["aggregate_result"], "REJECT")
        self.assertIn("raw_text_payload_field_present", _reason_codes(summary))

        event = build_valid_financial_event(model_output="model text")
        summary = validate_financial_event(event)
        self.assertEqual(summary["aggregate_result"], "REJECT")
        self.assertIn("raw_text_payload_field_present", _reason_codes(summary))

        pair = build_valid_claim_event_pair()
        pair["atomic_claim"]["model_output"] = "model text"
        summary = validate_claim_event_pair(pair["atomic_claim"], pair["financial_event"])
        self.assertEqual(summary["aggregate_result"], "REJECT")
        self.assertIn("raw_text_payload_field_present", _reason_codes(summary))

        output = build_valid_claim_event_compiler_output()
        output["financial_event"]["model_output"] = "model text"
        summary = _validate_compiler_output(output)
        self.assertEqual(summary["aggregate_result"], "REJECT")
        self.assertIn("raw_text_payload_field_present", _reason_codes(summary))

        claim = build_valid_atomic_claim(raw_text="synthetic inline text should be denied")
        summary = validate_atomic_claim(claim)
        self.assertEqual(summary["aggregate_result"], "REJECT")
        self.assertIn("raw_text_payload_field_present", _reason_codes(summary))

        event = build_valid_financial_event(trade_signal="synthetic_forbidden_trade_signal")
        summary = validate_financial_event(event)
        self.assertEqual(summary["aggregate_result"], "REJECT")
        self.assertIn("trade_signal_field_present", _reason_codes(summary))

        event = build_valid_financial_event(order_intent="synthetic_forbidden_order_intent")
        summary = validate_financial_event(event)
        self.assertEqual(summary["aggregate_result"], "REJECT")
        self.assertIn("order_intent_field_present", _reason_codes(summary))

        event = build_valid_financial_event(position_target="synthetic_forbidden_position_target")
        summary = validate_financial_event(event)
        self.assertEqual(summary["aggregate_result"], "REJECT")
        self.assertIn("position_target_field_present", _reason_codes(summary))

        event = build_valid_financial_event(execution_instruction="synthetic_forbidden_execution_instruction")
        summary = validate_financial_event(event)
        self.assertEqual(summary["aggregate_result"], "REJECT")
        self.assertIn("broker_execution_field_present", _reason_codes(summary))

        claim = build_valid_atomic_claim(claim_text_or_structured_predicate="sk-fixture-sentinel-0000000000")
        summary = validate_atomic_claim(claim)
        self.assertEqual(summary["aggregate_result"], "REJECT")
        self.assertIn("secret_like_value_detected", _reason_codes(summary))

        output = build_valid_claim_event_compiler_output()
        output["raw_evidence_record"]["prompt_injection_flags"] = ["prompt_injection_suspected"]
        summary = _validate_compiler_output(output)
        self.assertEqual(summary["aggregate_result"], "REJECT")
        self.assertIn("prompt_injection_quarantine_missing", _reason_codes(summary))

        event = build_valid_financial_event(non_claims=["synthetic_fixture_only"])
        summary = validate_financial_event(event)
        self.assertEqual(summary["aggregate_result"], "REJECT")
        self.assertIn("missing_mandatory_non_claims", _reason_codes(summary))

    def test_carry_forward_fields_required_and_consistent(self) -> None:
        for field in ("raw_storage_policy", "retention_policy", "source_trust_tier", "prompt_injection_flags"):
            with self.subTest(artifact="atomic_claim", field=field):
                claim = build_valid_atomic_claim()
                del claim[field]
                summary = validate_atomic_claim(claim)
                self.assertEqual(summary["aggregate_result"], "REJECT")
                self.assertIn("required_field_missing", _reason_codes(summary))

        for field in ("raw_storage_policy", "retention_policy", "source_trust_tier", "prompt_injection_flags"):
            with self.subTest(artifact="financial_event", field=field):
                event = build_valid_financial_event()
                del event[field]
                summary = validate_financial_event(event)
                self.assertEqual(summary["aggregate_result"], "REJECT")
                self.assertIn("required_field_missing", _reason_codes(summary))

        pair = build_valid_claim_event_pair()
        pair["financial_event"]["retention_policy"] = "synthetic_retention_mismatch"
        summary = validate_claim_event_pair(pair["atomic_claim"], pair["financial_event"])
        self.assertEqual(summary["aggregate_result"], "REJECT")
        self.assertIn("claim_event_carry_forward_mismatch", _reason_codes(summary))

        output = build_valid_claim_event_compiler_output()
        output["atomic_claim"]["raw_storage_policy"] = "metadata_only"
        summary = _validate_compiler_output(output)
        self.assertEqual(summary["aggregate_result"], "REJECT")
        self.assertIn("claim_event_carry_forward_mismatch", _reason_codes(summary))

        output = build_valid_claim_event_compiler_output()
        summary = _validate_compiler_output(output)
        self.assertEqual(summary["aggregate_result"], "ACCEPT")

    def test_synthetic_scope_and_future_authorization_fail_closed(self) -> None:
        claim = build_valid_atomic_claim(extraction_method="llm_candidate_future_authorization_required")
        summary = validate_atomic_claim(claim)
        self.assertEqual(summary["aggregate_result"], "REJECT")
        self.assertIn("synthetic_fixture_scope_invalid", _reason_codes(summary))

        claim = build_valid_atomic_claim(model_ref="synthetic_model_ref_future_node")
        summary = validate_atomic_claim(claim)
        self.assertEqual(summary["aggregate_result"], "REJECT")
        self.assertIn("synthetic_fixture_scope_invalid", _reason_codes(summary))

        event = build_valid_financial_event(event_derivation_method="llm_candidate_future_authorization_required")
        summary = validate_financial_event(event)
        self.assertEqual(summary["aggregate_result"], "REJECT")
        self.assertIn("synthetic_fixture_scope_invalid", _reason_codes(summary))

        event = build_valid_financial_event(event_type="rumor_or_unverified_event")
        summary = validate_financial_event(event)
        self.assertEqual(summary["aggregate_result"], "REJECT")
        self.assertIn("synthetic_fixture_scope_invalid", _reason_codes(summary))

    def test_no_silent_repair_and_input_immutability(self) -> None:
        claim = build_valid_atomic_claim()
        del claim["source_timestamp_ns"]
        before = deepcopy(claim)
        summary = validate_atomic_claim(claim)
        self.assertEqual(summary["aggregate_result"], "REJECT")
        self.assertEqual(claim, before)
        self.assertNotIn("source_timestamp_ns", claim)

        output = build_valid_claim_event_compiler_output()
        before = deepcopy(output)
        _validate_compiler_output(output)
        self.assertEqual(output, before)

    def test_aggregate_verdict_precedence_remains_a5_ordered(self) -> None:
        results = (
            ValidatorResult("a", ValidatorStatus.ACCEPT, "accepted"),
            ValidatorResult("b", ValidatorStatus.NEUTRALIZE, "neutralized"),
            ValidatorResult("c", ValidatorStatus.HOLD_REVIEW, "hold"),
            ValidatorResult("d", ValidatorStatus.REJECT, "reject"),
        )
        self.assertEqual(aggregate_validator_results(results), ValidatorStatus.REJECT)


def _validate_compiler_output(output: dict[str, object]) -> dict[str, object]:
    return validate_claim_event_compiler_output(
        output["atomic_claim_ledger"],
        output["atomic_claim"],
        output["financial_event_table"],
        output["financial_event"],
        output["raw_evidence_vault_manifest"],
        output["raw_evidence_record"],
        output["source_document_index"],
        output["source_manifest"],
        output["license_manifest"],
    )


def _validate_target(target: str, output: dict[str, object]) -> dict[str, object]:
    if target == "claim":
        return validate_atomic_claim(output["atomic_claim"])
    if target == "event":
        return validate_financial_event(output["financial_event"])
    if target == "pair":
        return validate_claim_event_pair(output["atomic_claim"], output["financial_event"])
    if target == "compiler_output":
        return _validate_compiler_output(output)
    raise AssertionError(f"unknown target {target}")


def _reason_codes(summary: dict[str, object]) -> set[str]:
    return {str(result["reason_code"]) for result in summary["validator_results"]}


def _load_json(path: Path) -> object:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _apply_mutations(output: dict[str, object], case: dict[str, object]) -> None:
    for path in case.get("delete", []):
        _delete_path(output, str(path))
    for path, value in case.get("set", {}).items():
        _set_path(output, str(path), value)


def _delete_path(root: dict[str, object], path: str) -> None:
    parent, key = _resolve_parent(root, path)
    del parent[key]


def _set_path(root: dict[str, object], path: str, value: object) -> None:
    parent, key = _resolve_parent(root, path)
    parent[key] = value


def _resolve_parent(root: dict[str, object], path: str) -> tuple[dict[str, object], str]:
    parts = path.split(".")
    current: object = root
    for part in parts[:-1]:
        if not isinstance(current, dict):
            raise AssertionError(f"non-dict path segment {part} in {path}")
        current = current[part]
    if not isinstance(current, dict):
        raise AssertionError(f"non-dict parent for {path}")
    return current, parts[-1]


if __name__ == "__main__":
    unittest.main()
