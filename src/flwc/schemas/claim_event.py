from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import Enum
from typing import Any

from flwc.schemas.common import SchemaIssue, ValidatorStatus
from flwc.schemas.source_license import LicenseState, RawStoragePolicy, RightsScope, SourceTrustTier


class ClaimType(str, Enum):
    ENTITY_ATTRIBUTE = "entity_attribute"
    FINANCIAL_METRIC = "financial_metric"
    CORPORATE_ACTION = "corporate_action"
    GUIDANCE_STATEMENT = "guidance_statement"
    CALENDAR_STATEMENT = "calendar_statement"
    POLICY_STATEMENT = "policy_statement"
    MARKET_STRUCTURE_STATEMENT = "market_structure_statement"
    RISK_DISCLOSURE = "risk_disclosure"
    MANAGEMENT_COMMENTARY = "management_commentary"
    MACRO_OBSERVATION = "macro_observation"
    SUPPLY_CHAIN_STATEMENT = "supply_chain_statement"
    LEGAL_REGULATORY_STATEMENT = "legal_regulatory_statement"
    CONFLICT_OR_DISPUTE = "conflict_or_dispute"
    OTHER = "other"


class ClaimExtractionMethod(str, Enum):
    MANUAL_FIXTURE = "manual_fixture"
    DETERMINISTIC_PARSER = "deterministic_parser"
    LLM_CANDIDATE_FUTURE_AUTHORIZATION_REQUIRED = "llm_candidate_future_authorization_required"
    HUMAN_REVIEW_PATCH = "human_review_patch"
    EXTERNAL_IMPORT_FUTURE_AUTHORIZATION_REQUIRED = "external_import_future_authorization_required"


class ClaimStatus(str, Enum):
    PROPOSED = "proposed"
    ACTIVE = "active"
    DISPUTED = "disputed"
    SUPERSEDED = "superseded"
    EXPIRED = "expired"
    RETRACTED = "retracted"
    REJECTED = "rejected"
    HOLD_REVIEW = "hold_review"
    NEUTRALIZED = "neutralized"


class FinancialEventType(str, Enum):
    EARNINGS_RELEASE = "earnings_release"
    GUIDANCE_UPDATE = "guidance_update"
    CORPORATE_ACTION = "corporate_action"
    MANAGEMENT_CHANGE = "management_change"
    REGULATORY_ACTION = "regulatory_action"
    LEGAL_ACTION = "legal_action"
    POLICY_DECISION = "policy_decision"
    MACRO_DATA_RELEASE = "macro_data_release"
    SUPPLY_CHAIN_EVENT = "supply_chain_event"
    PRODUCT_LAUNCH_OR_DELAY = "product_launch_or_delay"
    FINANCING_OR_DEBT_EVENT = "financing_or_debt_event"
    RATING_ACTION = "rating_action"
    MNA_EVENT = "mna_event"
    RISK_DISCLOSURE_EVENT = "risk_disclosure_event"
    CALENDAR_EVENT = "calendar_event"
    MARKET_STRUCTURE_EVENT = "market_structure_event"
    RUMOR_OR_UNVERIFIED_EVENT = "rumor_or_unverified_event"
    OTHER = "other"


class EventDirectionCandidate(str, Enum):
    POSITIVE_CANDIDATE = "positive_candidate"
    NEGATIVE_CANDIDATE = "negative_candidate"
    MIXED_CANDIDATE = "mixed_candidate"
    NEUTRAL_CANDIDATE = "neutral_candidate"
    UNKNOWN = "unknown"
    NOT_APPLICABLE = "not_applicable"


class FinancialEventStatus(str, Enum):
    PROPOSED = "proposed"
    ACTIVE = "active"
    DISPUTED = "disputed"
    SUPERSEDED = "superseded"
    EXPIRED = "expired"
    RETRACTED = "retracted"
    REJECTED = "rejected"
    HOLD_REVIEW = "hold_review"
    NEUTRALIZED = "neutralized"


class EventDerivationMethod(str, Enum):
    MANUAL_FIXTURE = "manual_fixture"
    DETERMINISTIC_RULE = "deterministic_rule"
    CLAIM_SET_COMPILER = "claim_set_compiler"
    LLM_CANDIDATE_FUTURE_AUTHORIZATION_REQUIRED = "llm_candidate_future_authorization_required"
    HUMAN_REVIEW_PATCH = "human_review_patch"


MANDATORY_CLAIM_EVENT_NON_CLAIMS = (
    "synthetic_fixture_only",
    "not_real_source",
    "not_source_ingestion",
    "not_truth_authority",
    "not_truth_oracle",
    "not_trade_signal",
    "not_order_intent",
    "not_position_sizing",
    "not_runtime_authority",
    "not_market_data_authority",
    "not_calibrated_probability",
    "not_execution_trigger",
    "not_real_claim_ledger",
    "not_real_event_table",
)

CLAIM_LEDGER_STRING_FIELDS = (
    "claim_ledger_id",
    "claim_ledger_version",
    "producer_id",
    "producer_version",
    "claim_digest",
    "lineage_digest",
)
CLAIM_LEDGER_POSITIVE_INT_FIELDS = ("source_cutoff_ns", "created_at_ns")
CLAIM_LEDGER_NONNEGATIVE_INT_FIELDS = ("claim_count",)
CLAIM_LEDGER_LIST_FIELDS = ("input_evidence_refs", "input_source_manifest_refs", "input_license_manifest_refs")

CLAIM_STRING_FIELDS = (
    "claim_id",
    "claim_version",
    "claim_text_or_structured_predicate",
    "predicate_id",
    "source_document_id",
    "source_manifest_ref",
    "license_manifest_ref",
    "retention_policy",
    "lineage_digest",
)
CLAIM_OPTIONAL_STRING_FIELDS = (
    "subject_entity_id",
    "object_unit",
    "model_ref",
    "prompt_template_ref",
    "human_review_ref",
    "superseded_by_claim_id",
)
CLAIM_LIST_FIELDS = ("source_span_refs", "raw_evidence_refs")
CLAIM_OPTIONAL_LIST_FIELDS = ("dispute_refs",)
CLAIM_REQUIRED_POSITIVE_INT_FIELDS = ("ingest_timestamp_ns", "available_from_ns", "compiler_seen_at_ns")
CLAIM_OPTIONAL_POSITIVE_INT_FIELDS = ("publisher_timestamp_ns", "source_timestamp_ns")

EVENT_TABLE_STRING_FIELDS = (
    "event_table_id",
    "event_table_version",
    "producer_id",
    "producer_version",
    "event_digest",
    "lineage_digest",
)
EVENT_TABLE_POSITIVE_INT_FIELDS = ("source_cutoff_ns", "created_at_ns")
EVENT_TABLE_NONNEGATIVE_INT_FIELDS = ("event_count",)
EVENT_TABLE_LIST_FIELDS = ("input_claim_ledger_refs", "input_source_manifest_refs", "input_license_manifest_refs")

EVENT_STRING_FIELDS = ("event_id", "event_version", "lineage_digest")
EVENT_CARRY_FORWARD_STRING_FIELDS = ("retention_policy",)
EVENT_OPTIONAL_STRING_FIELDS = ("primary_entity_id", "country_or_region", "sector", "asset_class")
EVENT_LIST_FIELDS = (
    "asset_refs",
    "evidence_claim_refs",
    "source_document_refs",
    "raw_evidence_refs",
    "source_manifest_refs",
    "license_manifest_refs",
)
EVENT_OPTIONAL_LIST_FIELDS = ("conflict_refs",)
EVENT_REQUIRED_POSITIVE_INT_FIELDS = ("available_from_ns", "compiler_seen_at_ns")
EVENT_OPTIONAL_POSITIVE_INT_FIELDS = ("event_time_ns", "publish_time_ns", "source_timestamp_ns")
EVENT_MAP_FIELDS = ("license_state_summary", "rights_scope_summary")
EVENT_OPTIONAL_SCORE_FIELDS = (
    "importance_score",
    "surprise_score",
    "novelty_score",
    "uncertainty_score",
    "confidence_score",
)


@dataclass(frozen=True)
class FLWCAtomicClaimLedgerV1:
    claim_ledger_id: str
    claim_ledger_version: str
    source_cutoff_ns: int
    created_at_ns: int
    producer_id: str
    producer_version: str
    claim_count: int
    claim_digest: str
    input_evidence_refs: tuple[str, ...]
    input_source_manifest_refs: tuple[str, ...]
    input_license_manifest_refs: tuple[str, ...]
    lineage_digest: str
    validation_status: ValidatorStatus
    validator_summary_ref: str | None
    non_claims: tuple[str, ...]
    schema_version: str = "FLWCAtomicClaimLedgerV1"

    @classmethod
    def from_mapping(cls, value: object) -> tuple["FLWCAtomicClaimLedgerV1 | None", tuple[SchemaIssue, ...]]:
        if not isinstance(value, Mapping):
            return None, (SchemaIssue("artifact_not_mapping", ("$",), "atomic claim ledger must be a JSON object"),)

        issues: list[SchemaIssue] = []
        schema_version = _require_exact_string(value, "schema_version", "FLWCAtomicClaimLedgerV1", issues)
        strings = {field: _require_string(value, field, issues) for field in CLAIM_LEDGER_STRING_FIELDS}
        positive_ints = {field: _require_positive_int(value, field, issues) for field in CLAIM_LEDGER_POSITIVE_INT_FIELDS}
        nonnegative_ints = {
            field: _require_nonnegative_int(value, field, issues) for field in CLAIM_LEDGER_NONNEGATIVE_INT_FIELDS
        }
        lists = {field: _require_string_list(value, field, issues, non_empty=True) for field in CLAIM_LEDGER_LIST_FIELDS}
        validation_status = _require_enum(value, "validation_status", ValidatorStatus, issues)
        validator_summary_ref = _require_optional_string(value, "validator_summary_ref", issues)
        non_claims = _require_string_list(value, "non_claims", issues, non_empty=True)
        if issues:
            return None, tuple(issues)
        return (
            cls(
                schema_version=schema_version,
                claim_ledger_id=strings["claim_ledger_id"],
                claim_ledger_version=strings["claim_ledger_version"],
                source_cutoff_ns=positive_ints["source_cutoff_ns"],
                created_at_ns=positive_ints["created_at_ns"],
                producer_id=strings["producer_id"],
                producer_version=strings["producer_version"],
                claim_count=nonnegative_ints["claim_count"],
                claim_digest=strings["claim_digest"],
                input_evidence_refs=lists["input_evidence_refs"],
                input_source_manifest_refs=lists["input_source_manifest_refs"],
                input_license_manifest_refs=lists["input_license_manifest_refs"],
                lineage_digest=strings["lineage_digest"],
                validation_status=validation_status,
                validator_summary_ref=validator_summary_ref,
                non_claims=non_claims,
            ),
            (),
        )

    def as_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "claim_ledger_id": self.claim_ledger_id,
            "claim_ledger_version": self.claim_ledger_version,
            "source_cutoff_ns": self.source_cutoff_ns,
            "created_at_ns": self.created_at_ns,
            "producer_id": self.producer_id,
            "producer_version": self.producer_version,
            "claim_count": self.claim_count,
            "claim_digest": self.claim_digest,
            "input_evidence_refs": list(self.input_evidence_refs),
            "input_source_manifest_refs": list(self.input_source_manifest_refs),
            "input_license_manifest_refs": list(self.input_license_manifest_refs),
            "lineage_digest": self.lineage_digest,
            "validation_status": self.validation_status.value,
            "validator_summary_ref": self.validator_summary_ref,
            "non_claims": list(self.non_claims),
        }


@dataclass(frozen=True)
class FLWCAtomicClaimV1:
    claim_id: str
    claim_version: str
    claim_type: ClaimType
    claim_text_or_structured_predicate: str
    subject_entity_id: str | None
    predicate_id: str
    object_value: Any
    object_unit: str | None
    time_scope: Any
    source_document_id: str
    source_span_refs: tuple[str, ...]
    raw_evidence_refs: tuple[str, ...]
    source_manifest_ref: str
    license_manifest_ref: str
    license_state: LicenseState
    rights_scope: RightsScope
    raw_storage_policy: RawStoragePolicy
    retention_policy: str
    source_trust_tier: SourceTrustTier
    prompt_injection_flags: tuple[str, ...]
    publisher_timestamp_ns: int | None
    source_timestamp_ns: int | None
    ingest_timestamp_ns: int
    available_from_ns: int
    compiler_seen_at_ns: int
    confidence_score: float | None
    extraction_method: ClaimExtractionMethod
    model_ref: str | None
    prompt_template_ref: str | None
    human_review_ref: str | None
    status: ClaimStatus
    superseded_by_claim_id: str | None
    dispute_refs: tuple[str, ...]
    lineage_digest: str
    validation_status: ValidatorStatus
    non_claims: tuple[str, ...]
    schema_version: str = "FLWCAtomicClaimV1"

    @classmethod
    def from_mapping(cls, value: object) -> tuple["FLWCAtomicClaimV1 | None", tuple[SchemaIssue, ...]]:
        if not isinstance(value, Mapping):
            return None, (SchemaIssue("artifact_not_mapping", ("$",), "atomic claim must be a JSON object"),)

        issues: list[SchemaIssue] = []
        schema_version = _require_exact_string(value, "schema_version", "FLWCAtomicClaimV1", issues)
        strings = {field: _require_string(value, field, issues) for field in CLAIM_STRING_FIELDS}
        optional_strings = {field: _require_optional_string(value, field, issues) for field in CLAIM_OPTIONAL_STRING_FIELDS}
        lists = {field: _require_string_list(value, field, issues, non_empty=True) for field in CLAIM_LIST_FIELDS}
        optional_lists = {
            field: _require_string_list(value, field, issues, non_empty=False) for field in CLAIM_OPTIONAL_LIST_FIELDS
        }
        required_ints = {field: _require_positive_int(value, field, issues) for field in CLAIM_REQUIRED_POSITIVE_INT_FIELDS}
        optional_ints = {
            field: _require_optional_positive_int(value, field, issues) for field in CLAIM_OPTIONAL_POSITIVE_INT_FIELDS
        }
        claim_type = _require_enum(value, "claim_type", ClaimType, issues)
        license_state = _require_enum(value, "license_state", LicenseState, issues)
        rights_scope = _require_enum(value, "rights_scope", RightsScope, issues)
        raw_storage_policy = _require_enum(value, "raw_storage_policy", RawStoragePolicy, issues)
        source_trust_tier = _require_enum(value, "source_trust_tier", SourceTrustTier, issues)
        prompt_injection_flags = _require_string_list(value, "prompt_injection_flags", issues, non_empty=False)
        extraction_method = _require_enum(value, "extraction_method", ClaimExtractionMethod, issues)
        status = _require_enum(value, "status", ClaimStatus, issues)
        validation_status = _require_enum(value, "validation_status", ValidatorStatus, issues)
        object_value = _require_json_value(value, "object_value", issues)
        time_scope = _require_optional_json_object(value, "time_scope", issues)
        confidence_score = _require_optional_score(value, "confidence_score", issues)
        non_claims = _require_string_list(value, "non_claims", issues, non_empty=True)
        if issues:
            return None, tuple(issues)
        return (
            cls(
                schema_version=schema_version,
                claim_id=strings["claim_id"],
                claim_version=strings["claim_version"],
                claim_type=claim_type,
                claim_text_or_structured_predicate=strings["claim_text_or_structured_predicate"],
                subject_entity_id=optional_strings["subject_entity_id"],
                predicate_id=strings["predicate_id"],
                object_value=object_value,
                object_unit=optional_strings["object_unit"],
                time_scope=time_scope,
                source_document_id=strings["source_document_id"],
                source_span_refs=lists["source_span_refs"],
                raw_evidence_refs=lists["raw_evidence_refs"],
                source_manifest_ref=strings["source_manifest_ref"],
                license_manifest_ref=strings["license_manifest_ref"],
                license_state=license_state,
                rights_scope=rights_scope,
                raw_storage_policy=raw_storage_policy,
                retention_policy=strings["retention_policy"],
                source_trust_tier=source_trust_tier,
                prompt_injection_flags=prompt_injection_flags,
                publisher_timestamp_ns=optional_ints["publisher_timestamp_ns"],
                source_timestamp_ns=optional_ints["source_timestamp_ns"],
                ingest_timestamp_ns=required_ints["ingest_timestamp_ns"],
                available_from_ns=required_ints["available_from_ns"],
                compiler_seen_at_ns=required_ints["compiler_seen_at_ns"],
                confidence_score=confidence_score,
                extraction_method=extraction_method,
                model_ref=optional_strings["model_ref"],
                prompt_template_ref=optional_strings["prompt_template_ref"],
                human_review_ref=optional_strings["human_review_ref"],
                status=status,
                superseded_by_claim_id=optional_strings["superseded_by_claim_id"],
                dispute_refs=optional_lists["dispute_refs"],
                lineage_digest=strings["lineage_digest"],
                validation_status=validation_status,
                non_claims=non_claims,
            ),
            (),
        )

    def as_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "claim_id": self.claim_id,
            "claim_version": self.claim_version,
            "claim_type": self.claim_type.value,
            "claim_text_or_structured_predicate": self.claim_text_or_structured_predicate,
            "subject_entity_id": self.subject_entity_id,
            "predicate_id": self.predicate_id,
            "object_value": _thaw_json_value(self.object_value),
            "object_unit": self.object_unit,
            "time_scope": _thaw_json_value(self.time_scope),
            "source_document_id": self.source_document_id,
            "source_span_refs": list(self.source_span_refs),
            "raw_evidence_refs": list(self.raw_evidence_refs),
            "source_manifest_ref": self.source_manifest_ref,
            "license_manifest_ref": self.license_manifest_ref,
            "license_state": self.license_state.value,
            "rights_scope": self.rights_scope.value,
            "raw_storage_policy": self.raw_storage_policy.value,
            "retention_policy": self.retention_policy,
            "source_trust_tier": self.source_trust_tier.value,
            "prompt_injection_flags": list(self.prompt_injection_flags),
            "publisher_timestamp_ns": self.publisher_timestamp_ns,
            "source_timestamp_ns": self.source_timestamp_ns,
            "ingest_timestamp_ns": self.ingest_timestamp_ns,
            "available_from_ns": self.available_from_ns,
            "compiler_seen_at_ns": self.compiler_seen_at_ns,
            "confidence_score": self.confidence_score,
            "extraction_method": self.extraction_method.value,
            "model_ref": self.model_ref,
            "prompt_template_ref": self.prompt_template_ref,
            "human_review_ref": self.human_review_ref,
            "status": self.status.value,
            "superseded_by_claim_id": self.superseded_by_claim_id,
            "dispute_refs": list(self.dispute_refs),
            "lineage_digest": self.lineage_digest,
            "validation_status": self.validation_status.value,
            "non_claims": list(self.non_claims),
        }


@dataclass(frozen=True)
class FLWCFinancialEventTableV1:
    event_table_id: str
    event_table_version: str
    source_cutoff_ns: int
    created_at_ns: int
    producer_id: str
    producer_version: str
    event_count: int
    event_digest: str
    input_claim_ledger_refs: tuple[str, ...]
    input_source_manifest_refs: tuple[str, ...]
    input_license_manifest_refs: tuple[str, ...]
    lineage_digest: str
    validation_status: ValidatorStatus
    validator_summary_ref: str | None
    non_claims: tuple[str, ...]
    schema_version: str = "FLWCFinancialEventTableV1"

    @classmethod
    def from_mapping(cls, value: object) -> tuple["FLWCFinancialEventTableV1 | None", tuple[SchemaIssue, ...]]:
        if not isinstance(value, Mapping):
            return None, (SchemaIssue("artifact_not_mapping", ("$",), "financial event table must be a JSON object"),)

        issues: list[SchemaIssue] = []
        schema_version = _require_exact_string(value, "schema_version", "FLWCFinancialEventTableV1", issues)
        strings = {field: _require_string(value, field, issues) for field in EVENT_TABLE_STRING_FIELDS}
        positive_ints = {field: _require_positive_int(value, field, issues) for field in EVENT_TABLE_POSITIVE_INT_FIELDS}
        nonnegative_ints = {
            field: _require_nonnegative_int(value, field, issues) for field in EVENT_TABLE_NONNEGATIVE_INT_FIELDS
        }
        lists = {field: _require_string_list(value, field, issues, non_empty=True) for field in EVENT_TABLE_LIST_FIELDS}
        validation_status = _require_enum(value, "validation_status", ValidatorStatus, issues)
        validator_summary_ref = _require_optional_string(value, "validator_summary_ref", issues)
        non_claims = _require_string_list(value, "non_claims", issues, non_empty=True)
        if issues:
            return None, tuple(issues)
        return (
            cls(
                schema_version=schema_version,
                event_table_id=strings["event_table_id"],
                event_table_version=strings["event_table_version"],
                source_cutoff_ns=positive_ints["source_cutoff_ns"],
                created_at_ns=positive_ints["created_at_ns"],
                producer_id=strings["producer_id"],
                producer_version=strings["producer_version"],
                event_count=nonnegative_ints["event_count"],
                event_digest=strings["event_digest"],
                input_claim_ledger_refs=lists["input_claim_ledger_refs"],
                input_source_manifest_refs=lists["input_source_manifest_refs"],
                input_license_manifest_refs=lists["input_license_manifest_refs"],
                lineage_digest=strings["lineage_digest"],
                validation_status=validation_status,
                validator_summary_ref=validator_summary_ref,
                non_claims=non_claims,
            ),
            (),
        )

    def as_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "event_table_id": self.event_table_id,
            "event_table_version": self.event_table_version,
            "source_cutoff_ns": self.source_cutoff_ns,
            "created_at_ns": self.created_at_ns,
            "producer_id": self.producer_id,
            "producer_version": self.producer_version,
            "event_count": self.event_count,
            "event_digest": self.event_digest,
            "input_claim_ledger_refs": list(self.input_claim_ledger_refs),
            "input_source_manifest_refs": list(self.input_source_manifest_refs),
            "input_license_manifest_refs": list(self.input_license_manifest_refs),
            "lineage_digest": self.lineage_digest,
            "validation_status": self.validation_status.value,
            "validator_summary_ref": self.validator_summary_ref,
            "non_claims": list(self.non_claims),
        }


@dataclass(frozen=True)
class FLWCFinancialEventV1:
    event_id: str
    event_version: str
    event_type: FinancialEventType
    event_time_ns: int | None
    publish_time_ns: int | None
    source_timestamp_ns: int | None
    available_from_ns: int
    compiler_seen_at_ns: int
    primary_entity_id: str | None
    asset_refs: tuple[str, ...]
    country_or_region: str | None
    sector: str | None
    asset_class: str | None
    evidence_claim_refs: tuple[str, ...]
    source_document_refs: tuple[str, ...]
    raw_evidence_refs: tuple[str, ...]
    source_manifest_refs: tuple[str, ...]
    license_manifest_refs: tuple[str, ...]
    license_state_summary: tuple[tuple[str, str], ...]
    rights_scope_summary: tuple[tuple[str, str], ...]
    raw_storage_policy: RawStoragePolicy
    retention_policy: str
    source_trust_tier: SourceTrustTier
    prompt_injection_flags: tuple[str, ...]
    direction_candidate: EventDirectionCandidate | None
    importance_score: float | None
    surprise_score: float | None
    novelty_score: float | None
    uncertainty_score: float | None
    confidence_score: float | None
    conflict_refs: tuple[str, ...]
    status: FinancialEventStatus
    event_derivation_method: EventDerivationMethod
    lineage_digest: str
    validation_status: ValidatorStatus
    non_claims: tuple[str, ...]
    schema_version: str = "FLWCFinancialEventV1"

    @classmethod
    def from_mapping(cls, value: object) -> tuple["FLWCFinancialEventV1 | None", tuple[SchemaIssue, ...]]:
        if not isinstance(value, Mapping):
            return None, (SchemaIssue("artifact_not_mapping", ("$",), "financial event must be a JSON object"),)

        issues: list[SchemaIssue] = []
        schema_version = _require_exact_string(value, "schema_version", "FLWCFinancialEventV1", issues)
        strings = {field: _require_string(value, field, issues) for field in EVENT_STRING_FIELDS}
        carry_forward_strings = {field: _require_string(value, field, issues) for field in EVENT_CARRY_FORWARD_STRING_FIELDS}
        optional_strings = {field: _require_optional_string(value, field, issues) for field in EVENT_OPTIONAL_STRING_FIELDS}
        lists = {field: _require_string_list(value, field, issues, non_empty=True) for field in EVENT_LIST_FIELDS}
        optional_lists = {
            field: _require_string_list(value, field, issues, non_empty=False) for field in EVENT_OPTIONAL_LIST_FIELDS
        }
        required_ints = {field: _require_positive_int(value, field, issues) for field in EVENT_REQUIRED_POSITIVE_INT_FIELDS}
        optional_ints = {
            field: _require_optional_positive_int(value, field, issues) for field in EVENT_OPTIONAL_POSITIVE_INT_FIELDS
        }
        maps = {field: _require_string_map(value, field, issues, non_empty=True) for field in EVENT_MAP_FIELDS}
        event_type = _require_enum(value, "event_type", FinancialEventType, issues)
        raw_storage_policy = _require_enum(value, "raw_storage_policy", RawStoragePolicy, issues)
        source_trust_tier = _require_enum(value, "source_trust_tier", SourceTrustTier, issues)
        prompt_injection_flags = _require_string_list(value, "prompt_injection_flags", issues, non_empty=False)
        direction_candidate = _require_optional_enum(value, "direction_candidate", EventDirectionCandidate, issues)
        status = _require_enum(value, "status", FinancialEventStatus, issues)
        event_derivation_method = _require_enum(value, "event_derivation_method", EventDerivationMethod, issues)
        validation_status = _require_enum(value, "validation_status", ValidatorStatus, issues)
        scores = {field: _require_optional_score(value, field, issues) for field in EVENT_OPTIONAL_SCORE_FIELDS}
        non_claims = _require_string_list(value, "non_claims", issues, non_empty=True)
        if issues:
            return None, tuple(issues)
        return (
            cls(
                schema_version=schema_version,
                event_id=strings["event_id"],
                event_version=strings["event_version"],
                event_type=event_type,
                event_time_ns=optional_ints["event_time_ns"],
                publish_time_ns=optional_ints["publish_time_ns"],
                source_timestamp_ns=optional_ints["source_timestamp_ns"],
                available_from_ns=required_ints["available_from_ns"],
                compiler_seen_at_ns=required_ints["compiler_seen_at_ns"],
                primary_entity_id=optional_strings["primary_entity_id"],
                asset_refs=lists["asset_refs"],
                country_or_region=optional_strings["country_or_region"],
                sector=optional_strings["sector"],
                asset_class=optional_strings["asset_class"],
                evidence_claim_refs=lists["evidence_claim_refs"],
                source_document_refs=lists["source_document_refs"],
                raw_evidence_refs=lists["raw_evidence_refs"],
                source_manifest_refs=lists["source_manifest_refs"],
                license_manifest_refs=lists["license_manifest_refs"],
                license_state_summary=maps["license_state_summary"],
                rights_scope_summary=maps["rights_scope_summary"],
                raw_storage_policy=raw_storage_policy,
                retention_policy=carry_forward_strings["retention_policy"],
                source_trust_tier=source_trust_tier,
                prompt_injection_flags=prompt_injection_flags,
                direction_candidate=direction_candidate,
                importance_score=scores["importance_score"],
                surprise_score=scores["surprise_score"],
                novelty_score=scores["novelty_score"],
                uncertainty_score=scores["uncertainty_score"],
                confidence_score=scores["confidence_score"],
                conflict_refs=optional_lists["conflict_refs"],
                status=status,
                event_derivation_method=event_derivation_method,
                lineage_digest=strings["lineage_digest"],
                validation_status=validation_status,
                non_claims=non_claims,
            ),
            (),
        )

    def as_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "event_id": self.event_id,
            "event_version": self.event_version,
            "event_type": self.event_type.value,
            "event_time_ns": self.event_time_ns,
            "publish_time_ns": self.publish_time_ns,
            "source_timestamp_ns": self.source_timestamp_ns,
            "available_from_ns": self.available_from_ns,
            "compiler_seen_at_ns": self.compiler_seen_at_ns,
            "primary_entity_id": self.primary_entity_id,
            "asset_refs": list(self.asset_refs),
            "country_or_region": self.country_or_region,
            "sector": self.sector,
            "asset_class": self.asset_class,
            "evidence_claim_refs": list(self.evidence_claim_refs),
            "source_document_refs": list(self.source_document_refs),
            "raw_evidence_refs": list(self.raw_evidence_refs),
            "source_manifest_refs": list(self.source_manifest_refs),
            "license_manifest_refs": list(self.license_manifest_refs),
            "license_state_summary": dict(self.license_state_summary),
            "rights_scope_summary": dict(self.rights_scope_summary),
            "raw_storage_policy": self.raw_storage_policy.value,
            "retention_policy": self.retention_policy,
            "source_trust_tier": self.source_trust_tier.value,
            "prompt_injection_flags": list(self.prompt_injection_flags),
            "direction_candidate": self.direction_candidate.value if self.direction_candidate else None,
            "importance_score": self.importance_score,
            "surprise_score": self.surprise_score,
            "novelty_score": self.novelty_score,
            "uncertainty_score": self.uncertainty_score,
            "confidence_score": self.confidence_score,
            "conflict_refs": list(self.conflict_refs),
            "status": self.status.value,
            "event_derivation_method": self.event_derivation_method.value,
            "lineage_digest": self.lineage_digest,
            "validation_status": self.validation_status.value,
            "non_claims": list(self.non_claims),
        }


def _field(prefix: str | None, field_name: str) -> str:
    return f"{prefix}.{field_name}" if prefix else field_name


def _missing(value: Mapping[str, Any], field_name: str, issues: list[SchemaIssue], *, field_prefix: str | None = None) -> bool:
    if field_name not in value:
        issues.append(SchemaIssue("required_field_missing", (_field(field_prefix, field_name),), "required field missing"))
        return True
    return False


def _require_string(value: Mapping[str, Any], field_name: str, issues: list[SchemaIssue], *, field_prefix: str | None = None) -> str:
    if _missing(value, field_name, issues, field_prefix=field_prefix):
        return ""
    field_value = value[field_name]
    if not isinstance(field_value, str) or not field_value.strip():
        issues.append(SchemaIssue("field_type_invalid", (_field(field_prefix, field_name),), "expected non-empty string"))
        return ""
    return field_value


def _require_exact_string(
    value: Mapping[str, Any],
    field_name: str,
    expected: str,
    issues: list[SchemaIssue],
    *,
    field_prefix: str | None = None,
) -> str:
    field_value = _require_string(value, field_name, issues, field_prefix=field_prefix)
    if field_value and field_value != expected:
        issues.append(SchemaIssue("schema_version_invalid", (_field(field_prefix, field_name),), f"expected {expected}"))
    return field_value


def _require_optional_string(
    value: Mapping[str, Any], field_name: str, issues: list[SchemaIssue], *, field_prefix: str | None = None
) -> str | None:
    if field_name not in value:
        return None
    field_value = value[field_name]
    if field_value is None:
        return None
    if not isinstance(field_value, str) or not field_value.strip():
        issues.append(SchemaIssue("field_type_invalid", (_field(field_prefix, field_name),), "expected string or null"))
        return None
    return field_value


def _require_positive_int(value: Mapping[str, Any], field_name: str, issues: list[SchemaIssue]) -> int:
    if _missing(value, field_name, issues):
        return 0
    field_value = value[field_name]
    if type(field_value) is not int or field_value <= 0:
        issues.append(SchemaIssue("field_type_invalid", (field_name,), "expected positive integer"))
        return 0
    return field_value


def _require_optional_positive_int(value: Mapping[str, Any], field_name: str, issues: list[SchemaIssue]) -> int | None:
    if field_name not in value:
        return None
    field_value = value[field_name]
    if field_value is None:
        return None
    if type(field_value) is not int or field_value <= 0:
        issues.append(SchemaIssue("field_type_invalid", (field_name,), "expected positive integer or null"))
        return None
    return field_value


def _require_nonnegative_int(value: Mapping[str, Any], field_name: str, issues: list[SchemaIssue]) -> int:
    if _missing(value, field_name, issues):
        return 0
    field_value = value[field_name]
    if type(field_value) is not int or field_value < 0:
        issues.append(SchemaIssue("field_type_invalid", (field_name,), "expected non-negative integer"))
        return 0
    return field_value


def _require_optional_score(value: Mapping[str, Any], field_name: str, issues: list[SchemaIssue]) -> float | None:
    if field_name not in value:
        return None
    field_value = value[field_name]
    if field_value is None:
        return None
    if isinstance(field_value, bool) or not isinstance(field_value, (int, float)):
        issues.append(SchemaIssue("field_type_invalid", (field_name,), "expected number or null"))
        return None
    return float(field_value)


def _require_string_list(
    value: Mapping[str, Any],
    field_name: str,
    issues: list[SchemaIssue],
    *,
    non_empty: bool,
) -> tuple[str, ...]:
    if _missing(value, field_name, issues):
        return ()
    field_value = value[field_name]
    if not isinstance(field_value, list) or any(not isinstance(item, str) or not item.strip() for item in field_value):
        issues.append(SchemaIssue("field_type_invalid", (field_name,), "expected list of non-empty strings"))
        return ()
    if non_empty and not field_value:
        issues.append(SchemaIssue("required_list_empty", (field_name,), "expected non-empty list"))
    return tuple(field_value)


def _require_string_map(
    value: Mapping[str, Any],
    field_name: str,
    issues: list[SchemaIssue],
    *,
    non_empty: bool,
) -> tuple[tuple[str, str], ...]:
    if _missing(value, field_name, issues):
        return ()
    field_value = value[field_name]
    if not isinstance(field_value, Mapping):
        issues.append(SchemaIssue("field_type_invalid", (field_name,), "expected map of non-empty strings"))
        return ()
    items: list[tuple[str, str]] = []
    for key, item in field_value.items():
        if not isinstance(key, str) or not key.strip() or not isinstance(item, str) or not item.strip():
            issues.append(SchemaIssue("field_type_invalid", (field_name,), "expected map of non-empty strings"))
            return ()
        items.append((key, item))
    if non_empty and not items:
        issues.append(SchemaIssue("required_map_empty", (field_name,), "expected non-empty map"))
    return tuple(sorted(items))


def _require_enum(value: Mapping[str, Any], field_name: str, enum_type: type[Enum], issues: list[SchemaIssue]) -> Any:
    raw_value = _require_string(value, field_name, issues)
    if not raw_value:
        return None
    try:
        return enum_type(raw_value)
    except ValueError:
        issues.append(SchemaIssue("enum_value_invalid", (field_name,), f"unsupported value {raw_value}"))
        return None


def _require_optional_enum(
    value: Mapping[str, Any], field_name: str, enum_type: type[Enum], issues: list[SchemaIssue]
) -> Any:
    if field_name not in value:
        return None
    raw_value = value[field_name]
    if raw_value is None:
        return None
    if not isinstance(raw_value, str) or not raw_value.strip():
        issues.append(SchemaIssue("field_type_invalid", (field_name,), "expected enum string or null"))
        return None
    try:
        return enum_type(raw_value)
    except ValueError:
        issues.append(SchemaIssue("enum_value_invalid", (field_name,), f"unsupported value {raw_value}"))
        return None


def _require_json_value(value: Mapping[str, Any], field_name: str, issues: list[SchemaIssue]) -> Any:
    if _missing(value, field_name, issues):
        return None
    try:
        return _freeze_json_value(value[field_name])
    except TypeError as exc:
        issues.append(SchemaIssue("field_type_invalid", (field_name,), str(exc)))
        return None


def _require_optional_json_object(value: Mapping[str, Any], field_name: str, issues: list[SchemaIssue]) -> Any:
    if field_name not in value:
        return None
    field_value = value[field_name]
    if field_value is None:
        return None
    if not isinstance(field_value, Mapping):
        issues.append(SchemaIssue("field_type_invalid", (field_name,), "expected object or null"))
        return None
    try:
        return _freeze_json_value(field_value)
    except TypeError as exc:
        issues.append(SchemaIssue("field_type_invalid", (field_name,), str(exc)))
        return None


def _freeze_json_value(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Mapping):
        items: list[tuple[str, Any]] = []
        for key, item in value.items():
            if not isinstance(key, str):
                raise TypeError("expected JSON object with string keys")
            items.append((key, _freeze_json_value(item)))
        return tuple(sorted(items))
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return tuple(_freeze_json_value(item) for item in value)
    raise TypeError("expected JSON scalar, object, list, or null")


def _thaw_json_value(value: Any) -> Any:
    if isinstance(value, tuple):
        if all(isinstance(item, tuple) and len(item) == 2 and isinstance(item[0], str) for item in value):
            return {key: _thaw_json_value(item) for key, item in value}
        return [_thaw_json_value(item) for item in value]
    return value


__all__ = [
    "ClaimExtractionMethod",
    "ClaimStatus",
    "ClaimType",
    "EventDerivationMethod",
    "EventDirectionCandidate",
    "FLWCAtomicClaimLedgerV1",
    "FLWCAtomicClaimV1",
    "FLWCFinancialEventTableV1",
    "FLWCFinancialEventV1",
    "FinancialEventStatus",
    "FinancialEventType",
    "MANDATORY_CLAIM_EVENT_NON_CLAIMS",
]
