from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from collections.abc import Iterable


class ValidatorStatus(str, Enum):
    ACCEPT = "ACCEPT"
    REJECT = "REJECT"
    HOLD_REVIEW = "HOLD_REVIEW"
    NEUTRALIZE = "NEUTRALIZE"


B0_VALIDATOR_VERSION = "FLWC-B0-FixtureValidator-0.0.0"
B0_VALIDATOR_RUN_ID = "flwc-b0-fixture-validator-run-001"
B0_VALIDATOR_RUN_NS = 1
B0_VALIDATOR_PRODUCER_ID = "flwc-b0-fixture-only"
B0_VALIDATOR_PRODUCER_VERSION = "0.0.0"
B0_VALIDATOR_NON_CLAIMS = (
    "fixture_validator_only",
    "not_accepted_evidence",
    "not_truth_authority",
    "not_source_authority",
    "not_license_authority",
    "not_runtime_authority",
    "not_external_admission_authority",
    "not_trade_signal",
    "not_order_intent",
    "not_position_sizing",
    "not_market_data_authority",
)

_ORDER = {
    ValidatorStatus.REJECT: 3,
    ValidatorStatus.HOLD_REVIEW: 2,
    ValidatorStatus.NEUTRALIZE: 1,
    ValidatorStatus.ACCEPT: 0,
}


@dataclass(frozen=True)
class ValidatorResult:
    validator_id: str
    result: ValidatorStatus
    reason_code: str
    reason_detail_bounded: str = ""
    field_refs: tuple[str, ...] = field(default_factory=tuple)
    validator_version: str = B0_VALIDATOR_VERSION
    artifact_ref: str = "unknown_artifact"
    artifact_schema_version: str = ""
    run_id: str = B0_VALIDATOR_RUN_ID
    run_started_at_ns: int = B0_VALIDATOR_RUN_NS
    run_completed_at_ns: int = B0_VALIDATOR_RUN_NS
    input_refs: tuple[str, ...] = field(default_factory=tuple)
    lineage_digest_checked: str | None = None
    non_claims_checked: tuple[str, ...] = field(default_factory=tuple)
    refusal_record_ref: str | None = None
    review_route_ref: str | None = None
    producer_id: str = B0_VALIDATOR_PRODUCER_ID
    non_claims: tuple[str, ...] = field(default_factory=tuple)

    def result_ref(self) -> str:
        return f"{self.artifact_ref}:{self.validator_id}:{self.reason_code}"

    def as_dict(self) -> dict[str, object]:
        return {
            "schema_version": "FLWCValidatorResultV1",
            "validator_id": self.validator_id,
            "validator_version": self.validator_version,
            "artifact_ref": self.artifact_ref,
            "artifact_schema_version": self.artifact_schema_version,
            "run_id": self.run_id,
            "run_started_at_ns": self.run_started_at_ns,
            "run_completed_at_ns": self.run_completed_at_ns,
            "result": self.result.value,
            "reason_code": self.reason_code,
            "reason_detail_bounded": self.reason_detail_bounded[:512],
            "field_refs": list(self.field_refs),
            "input_refs": list(self.input_refs),
            "lineage_digest_checked": self.lineage_digest_checked,
            "non_claims_checked": list(self.non_claims_checked),
            "refusal_record_ref": self.refusal_record_ref,
            "review_route_ref": self.review_route_ref,
            "producer_id": self.producer_id,
            "non_claims": list(self.non_claims),
        }


@dataclass(frozen=True)
class ValidatorSummary:
    validator_summary_id: str
    run_id: str
    input_artifact_refs: tuple[str, ...]
    validator_results: tuple[ValidatorResult, ...]
    aggregate_result: ValidatorStatus
    refusal_record_refs: tuple[str, ...] = field(default_factory=tuple)
    created_at_ns: int = B0_VALIDATOR_RUN_NS
    producer_id: str = B0_VALIDATOR_PRODUCER_ID
    producer_version: str = B0_VALIDATOR_PRODUCER_VERSION
    non_claims: tuple[str, ...] = B0_VALIDATOR_NON_CLAIMS

    @classmethod
    def from_results(
        cls,
        *,
        validator_summary_id: str,
        input_artifact_refs: tuple[str, ...],
        validator_results: tuple[ValidatorResult, ...],
    ) -> "ValidatorSummary":
        aggregate = ValidatorStatus.ACCEPT
        for result in validator_results:
            if _ORDER[result.result] > _ORDER[aggregate]:
                aggregate = result.result
        return cls(
            validator_summary_id=validator_summary_id,
            run_id=B0_VALIDATOR_RUN_ID,
            input_artifact_refs=input_artifact_refs,
            validator_results=validator_results,
            aggregate_result=aggregate,
        )

    def _count(self, status: ValidatorStatus) -> int:
        return sum(1 for result in self.validator_results if result.result == status)

    def as_dict(self) -> dict[str, object]:
        return {
            "schema_version": "FLWCValidatorSummaryV1",
            "validator_summary_id": self.validator_summary_id,
            "run_id": self.run_id,
            "input_artifact_refs": list(self.input_artifact_refs),
            "validator_result_refs": [result.result_ref() for result in self.validator_results],
            "refusal_record_refs": list(self.refusal_record_refs),
            "accepted_count": self._count(ValidatorStatus.ACCEPT),
            "rejected_count": self._count(ValidatorStatus.REJECT),
            "hold_review_count": self._count(ValidatorStatus.HOLD_REVIEW),
            "neutralized_count": self._count(ValidatorStatus.NEUTRALIZE),
            "aggregate_result": self.aggregate_result.value,
            "created_at_ns": self.created_at_ns,
            "producer_id": self.producer_id,
            "producer_version": self.producer_version,
            "validator_results": [result.as_dict() for result in self.validator_results],
            "non_claims": list(self.non_claims),
        }


def ensure_strings(values: object) -> tuple[str, ...]:
    if isinstance(values, str) or not isinstance(values, Iterable):
        return ()
    return tuple(v for v in values if isinstance(v, str))
