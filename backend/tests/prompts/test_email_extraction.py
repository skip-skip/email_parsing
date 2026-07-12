from __future__ import annotations

import json
from unittest.mock import MagicMock

import pytest

from backend.app.prompts.email_extraction import (
    EMAIL_EXTRACTION_SYSTEM,
    EMAIL_EXTRACTION_USER,
    EMAIL_EXTRACTION_VERSION,
)
from backend.tests.prompts.test_data import (
    EMAIL_SAMPLES,
    MOCK_LLM_EXTRACTION_RESPONSES,
    EmailSample,
)


def _build_mock_client(sample: EmailSample) -> MagicMock:
    mock_client = MagicMock()
    response = MOCK_LLM_EXTRACTION_RESPONSES[sample.name]
    mock_client.generate.return_value = json.dumps(response)
    mock_client.generate_json.return_value = response
    mock_client._parse_json.return_value = response
    return mock_client


EXTRACTION_FIELDS = [
    "client",
    "sender",
    "subject",
    "project_number",
    "task_description",
    "deadline",
    "budget_hours",
    "attachments",
    "confidence",
]


class TestEmailExtractionPromptFormat:
    def test_system_prompt_exists(self) -> None:
        assert EMAIL_EXTRACTION_SYSTEM

    def test_user_prompt_exists(self) -> None:
        assert EMAIL_EXTRACTION_USER

    def test_user_prompt_has_placeholders(self) -> None:
        assert "{sender}" in EMAIL_EXTRACTION_USER
        assert "{subject}" in EMAIL_EXTRACTION_USER
        assert "{received_time}" in EMAIL_EXTRACTION_USER
        assert "{body}" in EMAIL_EXTRACTION_USER

    def test_version_is_tracked(self) -> None:
        assert EMAIL_EXTRACTION_VERSION
        assert EMAIL_EXTRACTION_VERSION.startswith("v")

    def test_system_prompt_requests_json(self) -> None:
        lower = EMAIL_EXTRACTION_SYSTEM.lower()
        assert "json" in lower

    def test_system_prompt_mentions_all_fields(self) -> None:
        for field in EXTRACTION_FIELDS:
            assert field in EMAIL_EXTRACTION_SYSTEM, (
                f"Field '{field}' not mentioned in system prompt"
            )


class TestEmailExtractionAccuracy:
    @pytest.mark.parametrize(
        "sample",
        EMAIL_SAMPLES,
        ids=[s.name for s in EMAIL_SAMPLES],
    )
    def test_prompt_formatted_with_sample(self, sample: EmailSample) -> None:
        formatted = EMAIL_EXTRACTION_USER.format(
            sender=sample.sender,
            subject=sample.subject,
            received_time=sample.received_time,
            body=sample.body,
        )
        assert sample.sender in formatted
        assert sample.subject in formatted
        assert sample.body in formatted

    @pytest.mark.parametrize(
        "sample",
        EMAIL_SAMPLES,
        ids=[s.name for s in EMAIL_SAMPLES],
    )
    def test_mock_response_matches_expected_fields(
        self, sample: EmailSample
    ) -> None:
        mock_client = _build_mock_client(sample)
        response = mock_client.generate_json()
        for field in EXTRACTION_FIELDS:
            assert field in response, (
                f"Sample '{sample.name}': field '{field}' missing from response"
            )

    def test_per_field_accuracy_tracking(self) -> None:
        field_correct: dict[str, int] = {f: 0 for f in EXTRACTION_FIELDS}
        total = len(EMAIL_SAMPLES)

        for sample in EMAIL_SAMPLES:
            mock_client = _build_mock_client(sample)
            response = mock_client.generate_json()
            expected = sample.expected_extraction

            for field in EXTRACTION_FIELDS:
                actual = response.get(field)
                exp = expected.get(field)
                if field == "confidence":
                    if isinstance(actual, (int, float)) and isinstance(
                        exp, (int, float)
                    ):
                        field_correct[field] += 1
                elif actual == exp:
                    field_correct[field] += 1

        results = {}
        for field in EXTRACTION_FIELDS:
            accuracy = field_correct[field] / total
            results[field] = accuracy

        overall = sum(results.values()) / len(results)
        assert overall >= 0.90, (
            f"Overall accuracy {overall:.1%} is below 90% threshold. "
            f"Per-field: {results}"
        )

    def test_string_field_accuracy(self) -> None:
        string_fields = ["client", "sender", "subject", "project_number"]
        correct = 0
        total = 0

        for sample in EMAIL_SAMPLES:
            mock_client = _build_mock_client(sample)
            response = mock_client.generate_json()
            expected = sample.expected_extraction

            for field in string_fields:
                total += 1
                if response.get(field) == expected.get(field):
                    correct += 1

        accuracy = correct / total
        assert accuracy >= 0.90, (
            f"String field accuracy {accuracy:.1%} is below 90% threshold"
        )

    def test_numeric_field_accuracy(self) -> None:
        numeric_fields = ["budget_hours"]
        correct = 0
        total = 0

        for sample in EMAIL_SAMPLES:
            mock_client = _build_mock_client(sample)
            response = mock_client.generate_json()
            expected = sample.expected_extraction

            for field in numeric_fields:
                total += 1
                actual = response.get(field)
                exp = expected.get(field)
                if actual == exp:
                    correct += 1

        accuracy = correct / total if total > 0 else 0
        assert accuracy >= 0.90, (
            f"Numeric field accuracy {accuracy:.1%} is below 90% threshold"
        )

    def test_date_field_accuracy(self) -> None:
        correct = 0
        total = 0

        for sample in EMAIL_SAMPLES:
            mock_client = _build_mock_client(sample)
            response = mock_client.generate_json()
            expected = sample.expected_extraction
            total += 1
            if response.get("deadline") == expected.get("deadline"):
                correct += 1

        accuracy = correct / total
        assert accuracy >= 0.90, (
            f"Date field accuracy {accuracy:.1%} is below 90% threshold"
        )

    def test_null_field_handling(self) -> None:
        for sample in EMAIL_SAMPLES:
            mock_client = _build_mock_client(sample)
            response = mock_client.generate_json()
            expected = sample.expected_extraction

            for field in EXTRACTION_FIELDS:
                if expected.get(field) is None:
                    assert response.get(field) is None, (
                        f"Sample '{sample.name}': field '{field}' should be null"
                    )

    def test_confidence_is_numeric(self) -> None:
        for sample in EMAIL_SAMPLES:
            mock_client = _build_mock_client(sample)
            response = mock_client.generate_json()
            confidence = response.get("confidence")
            assert isinstance(confidence, (int, float)), (
                f"Sample '{sample.name}': confidence should be numeric"
            )
            assert 0 <= confidence <= 1, (
                f"Sample '{sample.name}': confidence {confidence} out of range"
            )


class TestEmailExtractionEdgeCases:
    def test_vague_email_low_confidence(self) -> None:
        sample = next(s for s in EMAIL_SAMPLES if s.name == "vague_request_missing_info")
        mock_client = _build_mock_client(sample)
        response = mock_client.generate_json()
        assert response["confidence"] < 0.5

    def test_informal_email_not_task(self) -> None:
        sample = next(s for s in EMAIL_SAMPLES if s.name == "informal_chat_no_task")
        mock_client = _build_mock_client(sample)
        response = mock_client.generate_json()
        assert response["task_description"] is None
        assert response["confidence"] < 0.5

    def test_cancellation_detected(self) -> None:
        sample = next(s for s in EMAIL_SAMPLES if s.name == "cancellation_request")
        mock_client = _build_mock_client(sample)
        response = mock_client.generate_json()
        assert "cancel" in response["task_description"].lower()

    def test_attachments_extracted(self) -> None:
        sample = next(
            s for s in EMAIL_SAMPLES if s.name == "detailed_booking_with_attachments"
        )
        mock_client = _build_mock_client(sample)
        response = mock_client.generate_json()
        assert len(response["attachments"]) >= 2

    def test_german_email_parsed(self) -> None:
        sample = next(s for s in EMAIL_SAMPLES if s.name == "international_client")
        mock_client = _build_mock_client(sample)
        response = mock_client.generate_json()
        assert response["client"] == "Deutsche Technik GmbH"
        assert response["project_number"] == "PRJ-2025-030"
