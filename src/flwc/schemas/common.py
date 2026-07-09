from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable


class ValidatorStatus(str, Enum):
    ACCEPT = "ACCEPT"
    REJECT = "REJECT"
    HOLD_REVIEW = "HOLD_REVIEW"
    NEUTRALIZE = "NEUTRALIZE"


@dataclass(frozen=True)
class ValidatorResult:
    validator_id: str
    result: ValidatorStatus
    reason_code: str
    reason_detail_bounded: str = ""
    field_refs: tuple[str, ...] = field(default_factory=tuple)
    non_claims: tuple[str, ...] = field(default_factory=tuple)

    def as_dict(self) -> dict[str, object]:
        return {
            "schema_version": "FLWCValidatorResultV1",
            "validator_id": self.validator_id,
            "result": self.result.value,
            "reason_code": self.reason_code,
            "reason_detail_bounded": self.reason_detail_bounded[:512],
            "field_refs": list(self.field_refs),
            "non_claims": list(self.non_claims),
        }


def ensure_strings(values: Iterable[object]) -> tuple[str, ...]:
    return tuple(v for v in values if isinstance(v, str))
