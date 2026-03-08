"""Tests for ARI scoring."""

import pytest

from src.governance.ari import apply_delta, band_for_score, clamp_score


def test_clamp_score_bounds() -> None:
    assert clamp_score(-10) == 0.0
    assert clamp_score(0) == 0.0
    assert clamp_score(50) == 50.0
    assert clamp_score(100) == 100.0
    assert clamp_score(150) == 100.0


def test_apply_delta() -> None:
    assert apply_delta(0, 15) == 15.0
    assert apply_delta(10, -0.5) == 9.5
    assert apply_delta(90, 20) == 100.0
    assert apply_delta(5, -10) == 0.0


def test_band_for_score() -> None:
    assert band_for_score(0) == "low"
    assert band_for_score(25) == "low"
    assert band_for_score(26) == "medium"
    assert band_for_score(50) == "medium"
    assert band_for_score(51) == "high"
    assert band_for_score(75) == "high"
    assert band_for_score(76) == "critical"
    assert band_for_score(100) == "critical"
