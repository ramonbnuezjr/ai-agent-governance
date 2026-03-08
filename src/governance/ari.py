"""Agency-Risk Index (ARI): per-session cumulative score 0-100 with bands."""

from typing import Literal

ARI_BAND = Literal["low", "medium", "high", "critical"]

# Bands: 0-25 Low, 26-50 Medium, 51-75 High, 76-100 Critical
BAND_LOW_MAX = 25.0
BAND_MEDIUM_MAX = 50.0
BAND_HIGH_MAX = 75.0


def clamp_score(score: float) -> float:
    """Clamp ARI score to [0, 100]."""
    if score < 0:
        return 0.0
    if score > 100:
        return 100.0
    return round(score, 2)


def apply_delta(current: float, delta: float) -> float:
    """Apply ARI impact delta and return new clamped score."""
    return clamp_score(current + delta)


def band_for_score(score: float) -> ARI_BAND:
    """Return band label for a score."""
    if score <= BAND_LOW_MAX:
        return "low"
    if score <= BAND_MEDIUM_MAX:
        return "medium"
    if score <= BAND_HIGH_MAX:
        return "high"
    return "critical"
