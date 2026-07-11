from __future__ import annotations

import json
import re
from collections.abc import Iterable
from typing import Any

from flwc.schemas.common import ValidatorResult, ValidatorStatus

_ORDER = {
    ValidatorStatus.REJECT: 3,
    ValidatorStatus.HOLD_REVIEW: 2,
    ValidatorStatus.NEUTRALIZE: 1,
    ValidatorStatus.ACCEPT: 0,
}


def aggregate_validator_results(results: Iterable[ValidatorResult]) -> ValidatorStatus:
    """A5 aggregation law: REJECT > HOLD_REVIEW > NEUTRALIZE > ACCEPT."""
    current = ValidatorStatus.ACCEPT
    for result in results:
        if _ORDER[result.result] > _ORDER[current]:
            current = result.result
    return current


SECRET_PATTERNS = (
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bghp_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b"),
)


def contains_secret_like_value(obj: Any) -> bool:
    text = json.dumps(obj, sort_keys=True, ensure_ascii=False)
    return any(pattern.search(text) for pattern in SECRET_PATTERNS)
