from __future__ import annotations

from copy import deepcopy
import json
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from flwc.compiler.raw_evidence_fixtures import (
    build_valid_raw_evidence_index_pair,
    build_valid_raw_evidence_record,
    build_valid_raw_evidence_vault_manifest,
    build_valid_source_document_index,
)
from flwc.schemas.common import ValidatorResult, ValidatorStatus
from flwc.schemas.raw_evidence import (
    FLWCRawEvidenceRecordV1,
    FLWCRawEvidenceVaultManifestV1,
    FLWCSourceDocumentIndexV1,
    QuarantineStatus,
    RawTextRefPolicy,
    VaultScope,
)
from flwc.validators.core import aggregate_validator_results
from flwc.validators.raw_evidence import (
    validate_raw_evidence_index_pair,
    validate_raw_evidence_index_pair_file,
    validate_raw_evidence_record,
    validate_raw_evidence_record_file,
    validate_raw_evidence_vault_manifest,
    validate_raw_evidence_vault_manifest_file,
    validate_source_document_index,
    validate_source_document_index_file,
)


class RawEvidenceValidatorTests(unittest.TestCase):
    def test_exact_a3_enum_acceptance_and_rejection(self) -> None:
        self.assertEqual(VaultScope("synthetic_fixture_only"), VaultScope.SYNTHETIC_FIXTURE_ONLY)
        self.assertEqual(RawTextRefPolicy("synthetic_fixture_text_allowed"), RawTextRefPolicy.SYNTHETIC_FIXTURE_TEXT_ALLOWED)
        self.assertEqual(QuarantineStatus("quarantined_for_prompt_injection"), QuarantineStatus.QUARANTINED_FOR_PROMPT_INJECTION)
        with self.assertRaises(ValueError):
            VaultScope("real_source_ingestion")
        with self.assertRaises(ValueError):
            RawTextRefPolicy("raw_text_runtime_enabled")
        with self.assertRaises(ValueError):
            QuarantineStatus("policy_override_allowed")

    def test_deterministic_builder_and_schema_round_trip(self) -> None:
        first_pair = build_valid_raw_evidence_index_pair()
        second_pair = build_valid_raw_evidence_index_pair()
        self.assertEqual(first_pair, second_pair)

        parsed_vault, vault_issues = FLWCRawEvidenceVaultManifestV1.from_mapping(first_pair["raw_evidence_vault_manifest"])
        parsed_record, record_issues = FLWCRawEvidenceRecordV1.from_mapping(first_pair["raw_evidence_record"])
        parsed_index, index_issues = FLWCSourceDocumentIndexV1.from_mapping(first_pair["source_document_index"])
        self.assertEqual(vault_issues, ())
        self.assertEqual(record_issues, ())
        self.assertEqual(index_issues, ())
        self.assertEqual(parsed_vault.as_dict(), first_pair["raw_evidence_vault_manifest"])
        self.assertEqual(parsed_record.as_dict(), first_pair["raw_evidence_record"])
        self.assertEqual(parsed_index.as_dict(), first_pair["source_document_index"])

    def test_valid_raw_evidence_vault_manifest_accepts(self) -> None:
        summary = validate_raw_evidence_vault_manifest_file(
            ROOT / "tests" / "fixtures" / "valid" / "raw_evidence_vault_manifest_valid.json"
        )
        self.assertEqual(summary["aggregate_result"], "ACCEPT")
        self.assertEqual(summary["rejected_count"], 0)

    def test_valid_raw_evidence_record_accepts(self) -> None:
        summary = validate_raw_evidence_record_file(ROOT / "tests" / "fixtures" / "valid" / "raw_evidence_record_valid.json")
        self.assertEqual(summary["aggregate_result"], "ACCEPT")
        self.assertEqual(summary["rejected_count"], 0)

    def test_valid_source_document_index_accepts(self) -> None:
        summary = validate_source_document_index_file(ROOT / "tests" / "fixtures" / "valid" / "source_document_index_valid.json")
        self.assertEqual(summary["aggregate_result"], "ACCEPT")
        self.assertEqual(summary["rejected_count"], 0)

    def test_valid_raw_evidence_index_pair_accepts(self) -> None:
        summary = validate_raw_evidence_index_pair_file(
            ROOT / "tests" / "fixtures" / "valid" / "raw_evidence_index_pair_valid.json"
        )
        self.assertEqual(summary["aggregate_result"], "ACCEPT")
        self.assertEqual(summary["rejected_count"], 0)

    def test_invalid_fixture_catalog_rejects_or_holds_with_expected_reason(self) -> None:
        cases = _load_json(ROOT / "tests" / "fixtures" / "invalid" / "raw_evidence_invalid_cases.json")
        for case in cases:
            with self.subTest(case_id=case["case_id"]):
                pair = build_valid_raw_evidence_index_pair()
                _apply_mutations(pair, case)
                summary = _validate_target(case["target"], pair)
                self.assertEqual(summary["aggregate_result"], case["expected_result"])
                self.assertIn(case["expected_reason_code"], _reason_codes(summary))

    def test_source_license_reference_and_pairing_enforcement(self) -> None:
        pair = build_valid_raw_evidence_index_pair()
        pair["raw_evidence_record"]["source_manifest_ref"] = "synthetic_source_manifest_mismatch"
        summary = _validate_pair(pair)
        self.assertEqual(summary["aggregate_result"], "REJECT")
        self.assertIn("raw_evidence_source_document_ref_mismatch", _reason_codes(summary))

        pair = build_valid_raw_evidence_index_pair()
        pair["license_manifest"]["source_id"] = "synthetic_source_mismatch"
        summary = _validate_pair(pair)
        self.assertEqual(summary["aggregate_result"], "REJECT")
        self.assertIn("source_license_pair_not_accepted", _reason_codes(summary))

    def test_rights_storage_and_retention_enforcement(self) -> None:
        record = build_valid_raw_evidence_record(rights_scope="derived_artifacts_internal_only")
        summary = validate_raw_evidence_record(record)
        self.assertEqual(summary["aggregate_result"], "REJECT")
        self.assertIn("rights_scope_raw_storage_incompatible", _reason_codes(summary))

        vault = build_valid_raw_evidence_vault_manifest(
            retention_policy_summary={"synthetic_source_manifest_001": "human_review_required"}
        )
        summary = validate_raw_evidence_vault_manifest(vault)
        self.assertEqual(summary["aggregate_result"], "HOLD_REVIEW")
        self.assertIn("retention_policy_requires_review", _reason_codes(summary))

        record = build_valid_raw_evidence_record(retention_policy="unknown")
        summary = validate_raw_evidence_record(record)
        self.assertEqual(summary["aggregate_result"], "HOLD_REVIEW")
        self.assertIn("retention_policy_requires_review", _reason_codes(summary))

    def test_timestamp_asof_hash_span_and_lineage_fail_closed(self) -> None:
        record = build_valid_raw_evidence_record(source_timestamp_ns=None)
        summary = validate_raw_evidence_record(record)
        self.assertEqual(summary["aggregate_result"], "REJECT")
        self.assertIn("source_timestamp_missing", _reason_codes(summary))

        pair = build_valid_raw_evidence_index_pair()
        pair["raw_evidence_record"]["available_from_ns"] = 1760000000000000999
        summary = _validate_pair(pair)
        self.assertEqual(summary["aggregate_result"], "REJECT")
        self.assertIn("available_from_after_source_cutoff", _reason_codes(summary))

        record = build_valid_raw_evidence_record(raw_text_hash=None)
        summary = validate_raw_evidence_record(record)
        self.assertEqual(summary["aggregate_result"], "REJECT")
        self.assertIn("raw_text_hash_missing", _reason_codes(summary))

        index = build_valid_source_document_index(document_hash=None)
        summary = validate_source_document_index(index)
        self.assertEqual(summary["aggregate_result"], "REJECT")
        self.assertIn("document_hash_missing", _reason_codes(summary))

        pair = build_valid_raw_evidence_index_pair()
        pair["raw_evidence_record"]["source_span_refs"] = ["synthetic_doc_001#segment:000002"]
        summary = _validate_pair(pair)
        self.assertEqual(summary["aggregate_result"], "REJECT")
        self.assertIn("source_document_segment_ref_invalid", _reason_codes(summary))

        record = build_valid_raw_evidence_record(lineage_digest="")
        summary = validate_raw_evidence_record(record)
        self.assertEqual(summary["aggregate_result"], "REJECT")
        self.assertIn("lineage_digest_missing", _reason_codes(summary))

    def test_prompt_injection_credential_non_claim_and_scope_enforcement(self) -> None:
        record = build_valid_raw_evidence_record(prompt_injection_flags=["prompt_injection_suspected"])
        summary = validate_raw_evidence_record(record)
        self.assertEqual(summary["aggregate_result"], "REJECT")
        self.assertIn("prompt_injection_quarantine_missing", _reason_codes(summary))

        record = build_valid_raw_evidence_record(
            prompt_injection_flags=["prompt_injection_suspected"],
            quarantine_status="quarantined_for_prompt_injection",
        )
        summary = validate_raw_evidence_record(record)
        self.assertEqual(summary["aggregate_result"], "HOLD_REVIEW")
        self.assertIn("prompt_injection_quarantined", _reason_codes(summary))

        index = build_valid_source_document_index(prompt_injection_flags=["prompt_injection_suspected"])
        summary = validate_source_document_index(index)
        self.assertEqual(summary["aggregate_result"], "REJECT")
        self.assertIn("prompt_injection_quarantine_missing", _reason_codes(summary))

        record = build_valid_raw_evidence_record(source_url_or_doc_id="sk-fixture-sentinel-0000000000")
        summary = validate_raw_evidence_record(record)
        self.assertEqual(summary["aggregate_result"], "REJECT")
        self.assertIn("secret_like_value_detected", _reason_codes(summary))

        index = build_valid_source_document_index(non_claims=["synthetic_fixture_only"])
        summary = validate_source_document_index(index)
        self.assertEqual(summary["aggregate_result"], "REJECT")
        self.assertIn("missing_mandatory_non_claims", _reason_codes(summary))

        vault = build_valid_raw_evidence_vault_manifest(vault_scope="authorized_source_future_node_only")
        summary = validate_raw_evidence_vault_manifest(vault)
        self.assertEqual(summary["aggregate_result"], "REJECT")
        self.assertIn("synthetic_fixture_scope_invalid", _reason_codes(summary))

    def test_inline_raw_text_payload_fields_reject(self) -> None:
        record = build_valid_raw_evidence_record(raw_text="synthetic inline text should be denied")
        summary = validate_raw_evidence_record(record)
        self.assertEqual(summary["aggregate_result"], "REJECT")
        self.assertIn("raw_text_payload_field_present", _reason_codes(summary))

        record = build_valid_raw_evidence_record(full_text="synthetic inline text should be denied")
        summary = validate_raw_evidence_record(record)
        self.assertEqual(summary["aggregate_result"], "REJECT")
        self.assertIn("raw_text_payload_field_present", _reason_codes(summary))

        index = build_valid_source_document_index(document_text="synthetic inline text should be denied")
        summary = validate_source_document_index(index)
        self.assertEqual(summary["aggregate_result"], "REJECT")
        self.assertIn("raw_text_payload_field_present", _reason_codes(summary))

        pair = build_valid_raw_evidence_index_pair()
        pair["raw_evidence_record"]["raw_text"] = "synthetic inline text should be denied"
        summary = _validate_pair(pair)
        self.assertEqual(summary["aggregate_result"], "REJECT")
        self.assertIn("raw_text_payload_field_present", _reason_codes(summary))

        pair = build_valid_raw_evidence_index_pair()
        pair["source_document_index"]["document_text"] = "synthetic inline text should be denied"
        summary = _validate_pair(pair)
        self.assertEqual(summary["aggregate_result"], "REJECT")
        self.assertIn("raw_text_payload_field_present", _reason_codes(summary))

    def test_raw_text_allowed_internal_rejects_in_b1_fixture_scope(self) -> None:
        record = build_valid_raw_evidence_record(raw_text_ref_policy="raw_text_allowed_internal")
        summary = validate_raw_evidence_record(record)
        self.assertEqual(summary["aggregate_result"], "REJECT")
        self.assertIn("synthetic_fixture_scope_invalid", _reason_codes(summary))

    def test_forbidden_boundary_fields_reject(self) -> None:
        record = build_valid_raw_evidence_record(claim_id="synthetic_claim_attempt")
        summary = validate_raw_evidence_record(record)
        self.assertEqual(summary["aggregate_result"], "REJECT")
        self.assertIn("forbidden_boundary_field_present", _reason_codes(summary))

        pair = build_valid_raw_evidence_index_pair()
        pair["raw_evidence_record"]["trade_signal"] = "synthetic_forbidden_trade_signal"
        summary = _validate_pair(pair)
        self.assertEqual(summary["aggregate_result"], "REJECT")
        self.assertIn("forbidden_boundary_field_present", _reason_codes(summary))

    def test_no_silent_repair_and_input_immutability(self) -> None:
        record = build_valid_raw_evidence_record()
        del record["source_timestamp_ns"]
        before = deepcopy(record)
        summary = validate_raw_evidence_record(record)
        self.assertEqual(summary["aggregate_result"], "REJECT")
        self.assertEqual(record, before)
        self.assertNotIn("source_timestamp_ns", record)

        pair = build_valid_raw_evidence_index_pair()
        before = deepcopy(pair)
        validate_raw_evidence_index_pair(
            pair["raw_evidence_vault_manifest"],
            pair["raw_evidence_record"],
            pair["source_document_index"],
            pair["source_manifest"],
            pair["license_manifest"],
        )
        self.assertEqual(pair, before)

    def test_aggregate_verdict_precedence_remains_a5_ordered(self) -> None:
        results = (
            ValidatorResult("a", ValidatorStatus.ACCEPT, "accepted"),
            ValidatorResult("b", ValidatorStatus.NEUTRALIZE, "neutralized"),
            ValidatorResult("c", ValidatorStatus.HOLD_REVIEW, "hold"),
            ValidatorResult("d", ValidatorStatus.REJECT, "reject"),
        )
        self.assertEqual(aggregate_validator_results(results), ValidatorStatus.REJECT)

    def test_validator_output_has_a5_fields_and_bounded_details(self) -> None:
        record = build_valid_raw_evidence_record()
        del record["evidence_id"]
        summary = validate_raw_evidence_record(record)
        schema_result = next(result for result in summary["validator_results"] if result["validator_id"] == "raw_evidence_schema_validator")
        self.assertEqual(schema_result["result"], "REJECT")
        self.assertIn("evidence_id", schema_result["field_refs"])
        self.assertLessEqual(len(schema_result["reason_detail_bounded"]), 512)
        self.assertIn("not_runtime_authority", schema_result["non_claims"])


def _load_json(path: Path) -> object:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _reason_codes(summary: dict[str, object]) -> list[str]:
    return [result["reason_code"] for result in summary["validator_results"]]


def _validate_target(target: str, pair: dict[str, object]) -> dict[str, object]:
    if target == "vault":
        return validate_raw_evidence_vault_manifest(pair["raw_evidence_vault_manifest"])
    if target == "record":
        return validate_raw_evidence_record(pair["raw_evidence_record"])
    if target == "index":
        return validate_source_document_index(pair["source_document_index"])
    if target == "pair":
        return _validate_pair(pair)
    raise AssertionError(f"unsupported target {target}")


def _validate_pair(pair: dict[str, object]) -> dict[str, object]:
    return validate_raw_evidence_index_pair(
        pair["raw_evidence_vault_manifest"],
        pair["raw_evidence_record"],
        pair["source_document_index"],
        pair["source_manifest"],
        pair["license_manifest"],
    )


def _apply_mutations(pair: dict[str, object], case: dict[str, object]) -> None:
    for field_ref in case.get("delete", []):
        _delete_path(pair, field_ref)
    for field_ref, value in case.get("set", {}).items():
        _set_path(pair, field_ref, value)


def _delete_path(value: dict[str, object], field_ref: str) -> None:
    parts = field_ref.split(".")
    current = value
    for part in parts[:-1]:
        current = current[part]
    del current[parts[-1]]


def _set_path(value: dict[str, object], field_ref: str, replacement: object) -> None:
    parts = field_ref.split(".")
    current = value
    for part in parts[:-1]:
        current = current[part]
    current[parts[-1]] = replacement


if __name__ == "__main__":
    unittest.main()
