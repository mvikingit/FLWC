from __future__ import annotations

from copy import deepcopy
import json
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from flwc.compiler.source_license_fixtures import (
    build_derived_only_license_manifest,
    build_human_review_required_license_manifest,
    build_metadata_only_license_manifest,
    build_valid_license_manifest,
    build_valid_source_license_pair,
    build_valid_source_manifest,
)
from flwc.schemas.common import ValidatorResult, ValidatorStatus
from flwc.schemas.source_license import (
    FLWCLicenseManifestV1,
    FLWCSourceManifestV1,
    LicenseState,
    RawStoragePolicy,
    RightsScope,
    SourceClass,
)
from flwc.validators.core import aggregate_validator_results
from flwc.validators.source_license import (
    validate_license_manifest,
    validate_license_manifest_file,
    validate_source_license_pair,
    validate_source_license_pair_file,
    validate_source_manifest,
    validate_source_manifest_file,
)


class SourceLicenseValidatorTests(unittest.TestCase):
    def test_exact_enum_acceptance_and_rejection(self) -> None:
        self.assertEqual(SourceClass("synthetic_fixture"), SourceClass.SYNTHETIC_FIXTURE)
        self.assertEqual(LicenseState("allowed_full_text"), LicenseState.ALLOWED_FULL_TEXT)
        self.assertEqual(RightsScope("research_internal_only"), RightsScope.RESEARCH_INTERNAL_ONLY)
        self.assertEqual(RawStoragePolicy("derived_fields_only"), RawStoragePolicy.DERIVED_FIELDS_ONLY)
        with self.assertRaises(ValueError):
            SourceClass("real_source")
        with self.assertRaises(ValueError):
            LicenseState("free_to_scrape")

    def test_deterministic_builder_and_schema_round_trip(self) -> None:
        first_pair = build_valid_source_license_pair()
        second_pair = build_valid_source_license_pair()
        self.assertEqual(first_pair, second_pair)

        parsed_source, source_issues = FLWCSourceManifestV1.from_mapping(first_pair["source_manifest"])
        parsed_license, license_issues = FLWCLicenseManifestV1.from_mapping(first_pair["license_manifest"])
        self.assertEqual(source_issues, ())
        self.assertEqual(license_issues, ())
        self.assertEqual(parsed_source.as_dict(), first_pair["source_manifest"])
        self.assertEqual(parsed_license.as_dict(), first_pair["license_manifest"])

    def test_valid_source_manifest_accepts(self) -> None:
        summary = validate_source_manifest_file(ROOT / "tests" / "fixtures" / "valid" / "source_manifest_valid.json")
        self.assertEqual(summary["aggregate_result"], "ACCEPT")
        self.assertEqual(summary["rejected_count"], 0)

    def test_valid_license_manifest_accepts(self) -> None:
        summary = validate_license_manifest_file(ROOT / "tests" / "fixtures" / "valid" / "license_manifest_valid.json")
        self.assertEqual(summary["aggregate_result"], "ACCEPT")
        self.assertEqual(summary["rejected_count"], 0)

    def test_valid_source_license_pair_accepts(self) -> None:
        summary = validate_source_license_pair_file(ROOT / "tests" / "fixtures" / "valid" / "source_license_pair_valid.json")
        self.assertEqual(summary["aggregate_result"], "ACCEPT")
        self.assertEqual(summary["rejected_count"], 0)

    def test_metadata_derived_and_human_review_fixture_variants(self) -> None:
        builders = {
            "metadata_only": build_metadata_only_license_manifest,
            "derived_only": build_derived_only_license_manifest,
            "human_review_required": build_human_review_required_license_manifest,
        }
        cases = _load_json(ROOT / "tests" / "fixtures" / "valid" / "source_license_variant_cases.json")
        for case in cases:
            with self.subTest(case_id=case["case_id"]):
                summary = validate_license_manifest(builders[case["builder"]]())
                self.assertEqual(summary["aggregate_result"], case["expected_result"])
                if "expected_reason_code" in case:
                    self.assertIn(case["expected_reason_code"], _reason_codes(summary))

    def test_invalid_fixture_catalog_rejects_or_holds_with_expected_reason(self) -> None:
        cases = _load_json(ROOT / "tests" / "fixtures" / "invalid" / "source_license_invalid_cases.json")
        for case in cases:
            with self.subTest(case_id=case["case_id"]):
                pair = build_valid_source_license_pair()
                _apply_mutations(pair, case)
                summary = _validate_target(case["target"], pair)
                self.assertEqual(summary["aggregate_result"], case["expected_result"])
                self.assertIn(case["expected_reason_code"], _reason_codes(summary))

    def test_source_license_pairing_mismatch_rejects(self) -> None:
        pair = build_valid_source_license_pair()
        pair["license_manifest"]["source_id"] = "synthetic_other_source"
        summary = validate_source_license_pair(pair["source_manifest"], pair["license_manifest"])
        self.assertEqual(summary["aggregate_result"], "REJECT")
        self.assertIn("source_license_source_id_mismatch", _reason_codes(summary))

    def test_unknown_forbidden_and_expired_license_behavior(self) -> None:
        cases = (
            ("unknown", "metadata_only", "HOLD_REVIEW", "license_state_requires_review"),
            ("unknown", "allowed_full_text", "REJECT", "unknown_license_raw_storage_requested"),
            ("forbidden", "metadata_only", "REJECT", "forbidden_license_state"),
            ("expired", "metadata_only", "REJECT", "expired_license_state_for_new_promotion"),
        )
        for state, storage, expected_result, expected_reason in cases:
            with self.subTest(state=state, storage=storage):
                manifest = build_valid_license_manifest(license_state=state, raw_storage_policy=storage)
                summary = validate_license_manifest(manifest)
                self.assertEqual(summary["aggregate_result"], expected_result)
                self.assertIn(expected_reason, _reason_codes(summary))

    def test_rights_scope_storage_and_retention_enforcement(self) -> None:
        source = build_valid_source_manifest(rights_scope="derived_artifacts_internal_only")
        summary = validate_source_manifest(source)
        self.assertEqual(summary["aggregate_result"], "REJECT")
        self.assertIn("rights_scope_raw_storage_incompatible", _reason_codes(summary))

        license_ = build_valid_license_manifest(retention_policy="unknown")
        summary = validate_license_manifest(license_)
        self.assertEqual(summary["aggregate_result"], "HOLD_REVIEW")
        self.assertIn("retention_policy_requires_review", _reason_codes(summary))

    def test_timestamp_hash_non_claim_and_synthetic_scope_fail_closed(self) -> None:
        source = build_valid_source_manifest()
        del source["source_timestamp_ns"]
        summary = validate_source_manifest(source)
        self.assertEqual(summary["aggregate_result"], "REJECT")
        self.assertIn("timestamp_field_missing_or_invalid", _reason_codes(summary))

        source = build_valid_source_manifest(raw_text_hash_required=True)
        summary = validate_source_manifest(source)
        self.assertEqual(summary["aggregate_result"], "REJECT")
        self.assertIn("raw_text_hash_missing", _reason_codes(summary))

        source = build_valid_source_manifest(non_claims=["synthetic_fixture_only"])
        summary = validate_source_manifest(source)
        self.assertEqual(summary["aggregate_result"], "REJECT")
        self.assertIn("missing_mandatory_non_claims", _reason_codes(summary))

        source = build_valid_source_manifest(source_class="official_source")
        summary = validate_source_manifest(source)
        self.assertEqual(summary["aggregate_result"], "REJECT")
        self.assertIn("synthetic_fixture_scope_invalid", _reason_codes(summary))

    def test_future_source_authorization_status_rejects_source_and_pair(self) -> None:
        source = build_valid_source_manifest(status="authorized_by_future_source_node")
        summary = validate_source_manifest(source)
        self.assertEqual(summary["aggregate_result"], "REJECT")
        self.assertIn("synthetic_fixture_status_not_accepted_metadata_only", _reason_codes(summary))

        pair = build_valid_source_license_pair()
        pair["source_manifest"]["status"] = "authorized_by_future_source_node"
        summary = validate_source_license_pair(pair["source_manifest"], pair["license_manifest"])
        self.assertEqual(summary["aggregate_result"], "REJECT")
        self.assertIn("synthetic_fixture_status_not_accepted_metadata_only", _reason_codes(summary))

    def test_unenumerated_source_policy_strings_fail_closed(self) -> None:
        source = build_valid_source_manifest(
            publisher_timestamp_policy="arbitrary_future_override",
            source_timestamp_policy="arbitrary_future_override",
        )
        summary = validate_source_manifest(source)
        self.assertEqual(summary["aggregate_result"], "REJECT")
        self.assertIn("source_policy_authority_escalation_rejected", _reason_codes(summary))

        source = build_valid_source_manifest(revision_policy="custom_review_policy")
        summary = validate_source_manifest(source)
        self.assertEqual(summary["aggregate_result"], "HOLD_REVIEW")
        self.assertIn("source_policy_value_unrecognized_requires_review", _reason_codes(summary))

        pair = build_valid_source_license_pair()
        pair["source_manifest"]["publisher_timestamp_policy"] = "arbitrary_future_override"
        pair["source_manifest"]["source_timestamp_policy"] = "arbitrary_future_override"
        summary = validate_source_license_pair(pair["source_manifest"], pair["license_manifest"])
        self.assertEqual(summary["aggregate_result"], "REJECT")
        self.assertIn("source_policy_authority_escalation_rejected", _reason_codes(summary))

    def test_unenumerated_license_policy_strings_fail_closed(self) -> None:
        license_ = build_valid_license_manifest(quote_policy="arbitrary_future_override")
        summary = validate_license_manifest(license_)
        self.assertEqual(summary["aggregate_result"], "REJECT")
        self.assertIn("license_policy_authority_escalation_rejected", _reason_codes(summary))

        license_ = build_valid_license_manifest(review_status="custom_review_policy")
        summary = validate_license_manifest(license_)
        self.assertEqual(summary["aggregate_result"], "HOLD_REVIEW")
        self.assertIn("license_policy_value_unrecognized_requires_review", _reason_codes(summary))

        pair = build_valid_source_license_pair()
        pair["license_manifest"]["quote_policy"] = "arbitrary_future_override"
        summary = validate_source_license_pair(pair["source_manifest"], pair["license_manifest"])
        self.assertEqual(summary["aggregate_result"], "REJECT")
        self.assertIn("license_policy_authority_escalation_rejected", _reason_codes(summary))

    def test_credential_like_value_refuses(self) -> None:
        license_ = build_valid_license_manifest(credential_reference_policy="sk-fixture-sentinel-0000000000")
        summary = validate_license_manifest(license_)
        self.assertEqual(summary["aggregate_result"], "REJECT")
        self.assertIn("secret_like_value_detected", _reason_codes(summary))

    def test_no_silent_repair_and_input_immutability(self) -> None:
        source = build_valid_source_manifest()
        del source["source_timestamp_ns"]
        before = deepcopy(source)
        summary = validate_source_manifest(source)
        self.assertEqual(summary["aggregate_result"], "REJECT")
        self.assertEqual(source, before)
        self.assertNotIn("source_timestamp_ns", source)

        license_ = build_valid_license_manifest()
        before = deepcopy(license_)
        validate_license_manifest(license_)
        self.assertEqual(license_, before)

    def test_aggregate_verdict_precedence_remains_a5_ordered(self) -> None:
        results = (
            ValidatorResult("a", ValidatorStatus.ACCEPT, "accepted"),
            ValidatorResult("b", ValidatorStatus.NEUTRALIZE, "neutralized"),
            ValidatorResult("c", ValidatorStatus.HOLD_REVIEW, "hold"),
            ValidatorResult("d", ValidatorStatus.REJECT, "reject"),
        )
        self.assertEqual(aggregate_validator_results(results), ValidatorStatus.REJECT)


def _load_json(path: Path) -> object:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _reason_codes(summary: dict[str, object]) -> list[str]:
    return [result["reason_code"] for result in summary["validator_results"]]


def _validate_target(target: str, pair: dict[str, object]) -> dict[str, object]:
    if target == "source":
        return validate_source_manifest(pair["source_manifest"])
    if target == "license":
        return validate_license_manifest(pair["license_manifest"])
    if target == "pair":
        return validate_source_license_pair(pair["source_manifest"], pair["license_manifest"])
    raise AssertionError(f"unsupported target {target}")


def _apply_mutations(pair: dict[str, object], case: dict[str, object]) -> None:
    for field_ref in case.get("delete", []):
        _delete_path(pair, field_ref)
    for field_ref, value in case.get("set", {}).items():
        _set_path(pair, field_ref, value)


def _delete_path(obj: dict[str, object], field_ref: str) -> None:
    current = obj
    parts = field_ref.split(".")
    for part in parts[:-1]:
        current = current[part]
    current.pop(parts[-1], None)


def _set_path(obj: dict[str, object], field_ref: str, value: object) -> None:
    current = obj
    parts = field_ref.split(".")
    for part in parts[:-1]:
        current = current[part]
    current[parts[-1]] = value


if __name__ == "__main__":
    unittest.main()
