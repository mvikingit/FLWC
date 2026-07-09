from __future__ import annotations

from collections.abc import Iterable

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
