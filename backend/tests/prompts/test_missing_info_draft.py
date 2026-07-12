from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from backend.app.prompts.missing_info_draft import (
    MISSING_INFO_DRAFT_SYSTEM,
    MISSING_INFO_DRAFT_USER,
    MISSING_INFO_DRAFT_VERSION,
)
from backend.tests.prompts.test_data import (
    EMAIL_SAMPLES,
    MISSING_INFO_DRAFT_TESTS,
    MOCK_MISSING_INFO_DRAFTS,
    MissingInfoDraftTest,
)


def _get_sample(sample_name: str):
    return next(s for s in EMAIL_SAMPLES if s.name == sample_name)


class TestMissingInfoDraftPromptFormat:
    def test_system_prompt_exists(self) -> None:
        assert MISSING_INFO_DRAFT_SYSTEM

    def test_user_prompt_exists(self) -> None:
        assert MISSING_INFO_DRAFT_USER

    def test_user_prompt_has_placeholders(self) -> None:
        assert "{sender}" in MISSING_INFO_DRAFT_USER
        assert "{subject}" in MISSING_INFO_DRAFT_USER
        assert "{missing_fields_list}" in MISSING_INFO_DRAFT_USER
        assert "{client}" in MISSING_INFO_DRAFT_USER
        assert "{project_number}" in MISSING_INFO_DRAFT_USER
        assert "{task_description}" in MISSING_INFO_DRAFT_USER

    def test_version_is_tracked(self) -> None:
        assert MISSING_INFO_DRAFT_VERSION
        assert MISSING_INFO_DRAFT_VERSION.startswith("v")

    def test_system_prompt_mentions_professionalism(self) -> None:
        lower = MISSING_INFO_DRAFT_SYSTEM.lower()
        assert "professional" in lower or "courteous" in lower

    def test_system_prompt_mentions_missing_info(self) -> None:
        lower = MISSING_INFO_DRAFT_SYSTEM.lower()
        assert "missing" in lower


class TestMissingInfoDraftQuality:
    @pytest.mark.parametrize(
        "draft_test",
        MISSING_INFO_DRAFT_TESTS,
        ids=[t.name for t in MISSING_INFO_DRAFT_TESTS],
    )
    def test_draft_contains_expected_keywords(
        self, draft_test: MissingInfoDraftTest
    ) -> None:
        draft = MOCK_MISSING_INFO_DRAFTS[draft_test.sample_name]
        draft_lower = draft.lower()
        for keyword in draft_test.expected_draft_keywords:
            assert keyword.lower() in draft_lower, (
                f"Draft for '{draft_test.name}' missing keyword: {keyword}"
            )

    @pytest.mark.parametrize(
        "draft_test",
        MISSING_INFO_DRAFT_TESTS,
        ids=[t.name for t in MISSING_INFO_DRAFT_TESTS],
    )
    def test_draft_does_not_contain_forbidden_words(
        self, draft_test: MissingInfoDraftTest
    ) -> None:
        draft = MOCK_MISSING_INFO_DRAFTS[draft_test.sample_name]
        draft_lower = draft.lower()
        for word in draft_test.expected_draft_forbidden:
            assert word.lower() not in draft_lower, (
                f"Draft for '{draft_test.name}' contains forbidden word: {word}"
            )

    def test_drafts_are_multi_sentence(self) -> None:
        for name, draft in MOCK_MISSING_INFO_DRAFTS.items():
            sentences = [s.strip() for s in draft.split(".") if s.strip()]
            assert len(sentences) >= 3, (
                f"Draft for '{name}' has only {len(sentences)} sentences, "
                "expected at least 3"
            )

    def test_drafts_mention_missing_fields(self) -> None:
        for test in MISSING_INFO_DRAFT_TESTS:
            draft = MOCK_MISSING_INFO_DRAFTS[test.sample_name]
            sample = _get_sample(test.sample_name)
            for field in sample.missing_fields:
                field_terms = field.replace("_", " ").lower()
                draft_lower = draft.lower()
                found = any(
                    term in draft_lower
                    for term in field_terms.split()
                    if len(term) > 3
                )
                assert found, (
                    f"Draft for '{test.name}' should reference missing field "
                    f"'{field}'"
                )

    def test_drafts_have_greeting(self) -> None:
        for name, draft in MOCK_MISSING_INFO_DRAFTS.items():
            has_greeting = any(
                draft.strip().startswith(prefix)
                for prefix in ["Dear", "Hi", "Hello", "Good"]
            )
            assert has_greeting, (
                f"Draft for '{name}' should start with a greeting"
            )

    def test_drafts_have_closing(self) -> None:
        for name, draft in MOCK_MISSING_INFO_DRAFTS.items():
            has_closing = any(
                word in draft.lower()
                for word in ["regards", "sincerely", "thank you", "best"]
            )
            assert has_closing, (
                f"Draft for '{name}' should have a professional closing"
            )

    def test_prompt_formatted_with_sample_data(self) -> None:
        sample = _get_sample("missing_project_number")
        formatted = MISSING_INFO_DRAFT_USER.format(
            sender=sample.sender,
            subject=sample.subject,
            missing_fields_list=", ".join(sample.missing_fields),
            client=sample.expected_extraction["client"],
            project_number=sample.expected_extraction["project_number"],
            task_description=sample.expected_extraction["task_description"],
        )
        assert sample.sender in formatted
        assert "project_number" in formatted

    def test_drafts_are_not_empty(self) -> None:
        for name, draft in MOCK_MISSING_INFO_DRAFTS.items():
            assert len(draft.strip()) > 50, (
                f"Draft for '{name}' is too short ({len(draft.strip())} chars)"
            )

    def test_drafts_are_not_too_long(self) -> None:
        for name, draft in MOCK_MISSING_INFO_DRAFTS.items():
            assert len(draft.strip()) < 2000, (
                f"Draft for '{name}' is too long ({len(draft.strip())} chars)"
            )

    def test_mock_client_returns_draft(self) -> None:
        mock_client = MagicMock()
        draft_text = MOCK_MISSING_INFO_DRAFTS["missing_project_number"]
        mock_client.generate.return_value = draft_text
        result = mock_client.generate("test prompt", "test system")
        assert "Bob" in result
        assert "project number" in result.lower()
