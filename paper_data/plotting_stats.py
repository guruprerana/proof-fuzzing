"""Small statistical helpers shared by the paper figures."""

from __future__ import annotations

import math
from statistics import NormalDist


def wilson_interval(
    successes: int,
    total: int,
    confidence: float = 0.95,
) -> tuple[float, float]:
    """Return a Wilson score interval for a binomial proportion."""
    if total <= 0:
        raise ValueError("total must be positive")
    if not 0 <= successes <= total:
        raise ValueError("successes must lie between zero and total")
    if not 0 < confidence < 1:
        raise ValueError("confidence must lie strictly between zero and one")

    z = NormalDist().inv_cdf(0.5 + confidence / 2)
    proportion = successes / total
    denominator = 1 + z * z / total
    center = (proportion + z * z / (2 * total)) / denominator
    half_width = (
        z
        * math.sqrt(
            proportion * (1 - proportion) / total
            + z * z / (4 * total * total)
        )
        / denominator
    )
    low = 0.0 if successes == 0 else max(0.0, center - half_width)
    high = 1.0 if successes == total else min(1.0, center + half_width)
    return low, high
