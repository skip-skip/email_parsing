from __future__ import annotations

import pytest

from backend.app.services.confidence import (
    ConfidenceThresholds,
    classify_confidence,
    get_confidence_indicator,
    get_review_requirements,
    get_thresholds,
    set_thresholds,
)


class TestConfidenceThresholds:
    def test_default_thresholds(self) -> None:
        t = ConfidenceThresholds()
        assert t.high == 0.95
        assert t.medium == 0.80
        assert t.low == 0.00

    def test_custom_thresholds(self) -> None:
        t = ConfidenceThresholds(high=0.9, medium=0.7, low=0.1)
        assert t.high == 0.9
        assert t.medium == 0.7
        assert t.low == 0.1

    def test_invalid_thresholds_raise(self) -> None:
        with pytest.raises(ValueError):
            ConfidenceThresholds(high=0.5, medium=0.9, low=0.0)
        with pytest.raises(ValueError):
            ConfidenceThresholds(high=1.1, medium=0.8, low=0.0)


class TestClassifyConfidence:
    def test_high_confidence(self) -> None:
        assert classify_confidence(0.95) == "HIGH"
        assert classify_confidence(1.0) == "HIGH"
        assert classify_confidence(0.98) == "HIGH"

    def test_medium_confidence(self) -> None:
        assert classify_confidence(0.80) == "MEDIUM"
        assert classify_confidence(0.85) == "MEDIUM"
        assert classify_confidence(0.94) == "MEDIUM"

    def test_low_confidence(self) -> None:
        assert classify_confidence(0.0) == "LOW"
        assert classify_confidence(0.5) == "LOW"
        assert classify_confidence(0.79) == "LOW"

    def test_clamping_above_one(self) -> None:
        assert classify_confidence(1.5) == "HIGH"
        assert classify_confidence(2.0) == "HIGH"

    def test_clamping_below_zero(self) -> None:
        assert classify_confidence(-0.1) == "LOW"
        assert classify_confidence(-1.0) == "LOW"

    def test_boundary_medium_to_high(self) -> None:
        assert classify_confidence(0.949) == "MEDIUM"
        assert classify_confidence(0.95) == "HIGH"

    def test_boundary_low_to_medium(self) -> None:
        assert classify_confidence(0.799) == "LOW"
        assert classify_confidence(0.80) == "MEDIUM"


class TestReviewRequirements:
    def test_high_confidence_requirements(self) -> None:
        reqs = get_review_requirements("HIGH")
        assert reqs.requires_manual_review is False
        assert reqs.can_auto_approve is True
        assert reqs.requires_additional_verification is False
        assert reqs.review_level == "minimal"

    def test_medium_confidence_requirements(self) -> None:
        reqs = get_review_requirements("MEDIUM")
        assert reqs.requires_manual_review is True
        assert reqs.can_auto_approve is False
        assert reqs.requires_additional_verification is False
        assert reqs.review_level == "standard"

    def test_low_confidence_requirements(self) -> None:
        reqs = get_review_requirements("LOW")
        assert reqs.requires_manual_review is True
        assert reqs.can_auto_approve is False
        assert reqs.requires_additional_verification is True
        assert reqs.review_level == "thorough"

    def test_unknown_classification_defaults_to_low(self) -> None:
        reqs = get_review_requirements("UNKNOWN")
        assert reqs.requires_manual_review is True
        assert reqs.can_auto_approve is False
        assert reqs.requires_additional_verification is True
        assert reqs.review_level == "thorough"


class TestConfigurableThresholds:
    def test_set_and_get_thresholds(self) -> None:
        original = get_thresholds()
        try:
            set_thresholds(high=0.9, medium=0.7, low=0.2)
            t = get_thresholds()
            assert t.high == 0.9
            assert t.medium == 0.7
            assert t.low == 0.2

            assert classify_confidence(0.9) == "HIGH"
            assert classify_confidence(0.7) == "MEDIUM"
            assert classify_confidence(0.6) == "LOW"
            assert classify_confidence(0.19) == "LOW"
        finally:
            set_thresholds(
                high=original.high,
                medium=original.medium,
                low=original.low,
            )

    def test_set_thresholds_validation(self) -> None:
        original = get_thresholds()
        try:
            with pytest.raises(ValueError):
                set_thresholds(high=0.5, medium=0.9, low=0.0)
        finally:
            set_thresholds(
                high=original.high,
                medium=original.medium,
                low=original.low,
            )


class TestConfidenceIndicator:
    def test_high_indicator(self) -> None:
        indicator = get_confidence_indicator(0.96)
        assert indicator["level"] == "HIGH"
        assert indicator["label"] == "HIGH Confidence"
        assert indicator["color"] == "green"

    def test_medium_indicator(self) -> None:
        indicator = get_confidence_indicator(0.85)
        assert indicator["level"] == "MEDIUM"
        assert indicator["label"] == "MEDIUM Confidence"
        assert indicator["color"] == "amber"

    def test_low_indicator(self) -> None:
        indicator = get_confidence_indicator(0.3)
        assert indicator["level"] == "LOW"
        assert indicator["label"] == "LOW Confidence"
        assert indicator["color"] == "red"

    def test_boundary_values(self) -> None:
        assert get_confidence_indicator(0.95)["level"] == "HIGH"
        assert get_confidence_indicator(0.80)["level"] == "MEDIUM"
        assert get_confidence_indicator(0.0)["level"] == "LOW"
