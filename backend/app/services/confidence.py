from __future__ import annotations

from dataclasses import dataclass

HIGH_CONFIDENCE = 0.95
MEDIUM_CONFIDENCE = 0.80
LOW_CONFIDENCE = 0.00


@dataclass
class ReviewRequirements:
    requires_manual_review: bool
    can_auto_approve: bool
    requires_additional_verification: bool
    review_level: str


DEFAULT_REVIEW_REQUIREMENTS: dict[str, ReviewRequirements] = {
    "HIGH": ReviewRequirements(
        requires_manual_review=False,
        can_auto_approve=True,
        requires_additional_verification=False,
        review_level="minimal",
    ),
    "MEDIUM": ReviewRequirements(
        requires_manual_review=True,
        can_auto_approve=False,
        requires_additional_verification=False,
        review_level="standard",
    ),
    "LOW": ReviewRequirements(
        requires_manual_review=True,
        can_auto_approve=False,
        requires_additional_verification=True,
        review_level="thorough",
    ),
}


class ConfidenceThresholds:
    def __init__(
        self,
        high: float = HIGH_CONFIDENCE,
        medium: float = MEDIUM_CONFIDENCE,
        low: float = LOW_CONFIDENCE,
    ) -> None:
        if not (0.0 <= low <= medium <= high <= 1.0):
            raise ValueError(
                "Thresholds must satisfy: 0.0 <= low <= medium <= high <= 1.0"
            )
        self.high = high
        self.medium = medium
        self.low = low

    def classify(self, confidence: float) -> str:
        clamped = max(0.0, min(1.0, confidence))
        if clamped >= self.high:
            return "HIGH"
        if clamped >= self.medium:
            return "MEDIUM"
        return "LOW"


_thresholds = ConfidenceThresholds()


def get_thresholds() -> ConfidenceThresholds:
    return _thresholds


def set_thresholds(
    high: float = HIGH_CONFIDENCE,
    medium: float = MEDIUM_CONFIDENCE,
    low: float = LOW_CONFIDENCE,
) -> None:
    global _thresholds
    _thresholds = ConfidenceThresholds(high=high, medium=medium, low=low)


def classify_confidence(confidence: float) -> str:
    return _thresholds.classify(confidence)


def get_review_requirements(classification: str) -> ReviewRequirements:
    return DEFAULT_REVIEW_REQUIREMENTS.get(
        classification,
        DEFAULT_REVIEW_REQUIREMENTS["LOW"],
    )


def get_confidence_indicator(confidence: float) -> dict[str, str]:
    classification = classify_confidence(confidence)
    return {
        "level": classification,
        "label": f"{classification} Confidence",
        "color": {"HIGH": "green", "MEDIUM": "amber", "LOW": "red"}.get(
            classification, "gray"
        ),
    }
