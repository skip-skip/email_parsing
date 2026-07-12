from __future__ import annotations

import json
from unittest.mock import MagicMock

import pytest

from backend.app.prompts.schedule_suggestion import (
    SCHEDULE_SUGGESTION_SYSTEM,
    SCHEDULE_SUGGESTION_USER,
    SCHEDULE_SUGGESTION_VERSION,
)
from backend.tests.prompts.test_data import (
    EMAIL_SAMPLES,
    MOCK_SCHEDULE_SUGGESTIONS,
    SCHEDULE_SUGGESTION_TESTS,
    ScheduleSuggestionTest,
)


def _get_sample(sample_name: str):
    return next(s for s in EMAIL_SAMPLES if s.name == sample_name)


class TestScheduleSuggestionPromptFormat:
    def test_system_prompt_exists(self) -> None:
        assert SCHEDULE_SUGGESTION_SYSTEM

    def test_user_prompt_exists(self) -> None:
        assert SCHEDULE_SUGGESTION_USER

    def test_user_prompt_has_placeholders(self) -> None:
        assert "{task_description}" in SCHEDULE_SUGGESTION_USER
        assert "{budget_hours}" in SCHEDULE_SUGGESTION_USER
        assert "{deadline}" in SCHEDULE_SUGGESTION_USER
        assert "{existing_events}" in SCHEDULE_SUGGESTION_USER

    def test_version_is_tracked(self) -> None:
        assert SCHEDULE_SUGGESTION_VERSION
        assert SCHEDULE_SUGGESTION_VERSION.startswith("v")

    def test_system_prompt_requests_json(self) -> None:
        lower = SCHEDULE_SUGGESTION_SYSTEM.lower()
        assert "json" in lower

    def test_system_prompt_mentions_blocks(self) -> None:
        lower = SCHEDULE_SUGGESTION_SYSTEM.lower()
        assert "block" in lower

    def test_system_prompt_mentions_working_hours(self) -> None:
        lower = SCHEDULE_SUGGESTION_USER.lower()
        assert "9:00" in lower or "9:00-17:00" in lower


class TestScheduleSuggestionStructure:
    @pytest.mark.parametrize(
        "sched_test",
        SCHEDULE_SUGGESTION_TESTS,
        ids=[t.name for t in SCHEDULE_SUGGESTION_TESTS],
    )
    def test_suggestion_has_required_keys(
        self, sched_test: ScheduleSuggestionTest
    ) -> None:
        suggestion = MOCK_SCHEDULE_SUGGESTIONS[sched_test.sample_name]
        assert "suggested_blocks" in suggestion
        assert "total_scheduled_hours" in suggestion
        assert "notes" in suggestion

    @pytest.mark.parametrize(
        "sched_test",
        SCHEDULE_SUGGESTION_TESTS,
        ids=[t.name for t in SCHEDULE_SUGGESTION_TESTS],
    )
    def test_suggested_blocks_have_correct_structure(
        self, sched_test: ScheduleSuggestionTest
    ) -> None:
        suggestion = MOCK_SCHEDULE_SUGGESTIONS[sched_test.sample_name]
        for block in suggestion["suggested_blocks"]:
            assert "day" in block
            assert "start_time" in block
            assert "end_time" in block
            assert "duration_hours" in block

    @pytest.mark.parametrize(
        "sched_test",
        SCHEDULE_SUGGESTION_TESTS,
        ids=[t.name for t in SCHEDULE_SUGGESTION_TESTS],
    )
    def test_suggested_blocks_have_valid_times(
        self, sched_test: ScheduleSuggestionTest
    ) -> None:
        suggestion = MOCK_SCHEDULE_SUGGESTIONS[sched_test.sample_name]
        for block in suggestion["suggested_blocks"]:
            start = block["start_time"]
            end = block["end_time"]
            assert len(start) == 5, f"Invalid start_time format: {start}"
            assert len(end) == 5, f"Invalid end_time format: {end}"
            assert start[2] == ":", f"Invalid start_time format: {start}"
            assert end[2] == ":", f"Invalid end_time format: {end}"
            assert start < end, (
                f"start_time {start} must be before end_time {end}"
            )

    @pytest.mark.parametrize(
        "sched_test",
        SCHEDULE_SUGGESTION_TESTS,
        ids=[t.name for t in SCHEDULE_SUGGESTION_TESTS],
    )
    def test_suggested_blocks_within_working_hours(
        self, sched_test: ScheduleSuggestionTest
    ) -> None:
        suggestion = MOCK_SCHEDULE_SUGGESTIONS[sched_test.sample_name]
        for block in suggestion["suggested_blocks"]:
            start_h, start_m = map(int, block["start_time"].split(":"))
            end_h, end_m = map(int, block["end_time"].split(":"))
            assert start_h >= 9, (
                f"Block starts before working hours: {block['start_time']}"
            )
            assert end_h <= 17, (
                f"Block ends after working hours: {block['end_time']}"
            )

    @pytest.mark.parametrize(
        "sched_test",
        SCHEDULE_SUGGESTION_TESTS,
        ids=[t.name for t in SCHEDULE_SUGGESTION_TESTS],
    )
    def test_total_hours_positive(
        self, sched_test: ScheduleSuggestionTest
    ) -> None:
        suggestion = MOCK_SCHEDULE_SUGGESTIONS[sched_test.sample_name]
        assert suggestion["total_scheduled_hours"] > 0

    @pytest.mark.parametrize(
        "sched_test",
        SCHEDULE_SUGGESTION_TESTS,
        ids=[t.name for t in SCHEDULE_SUGGESTION_TESTS],
    )
    def test_minimum_block_count(
        self, sched_test: ScheduleSuggestionTest
    ) -> None:
        suggestion = MOCK_SCHEDULE_SUGGESTIONS[sched_test.sample_name]
        assert len(suggestion["suggested_blocks"]) >= sched_test.expected_min_blocks


class TestScheduleSuggestionFeasibility:
    def test_valid_days_of_week(self) -> None:
        valid_days = {
            "Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
            "Saturday", "Sunday",
        }
        for name, suggestion in MOCK_SCHEDULE_SUGGESTIONS.items():
            for block in suggestion["suggested_blocks"]:
                assert block["day"] in valid_days, (
                    f"Suggestion '{name}': invalid day '{block['day']}'"
                )

    def test_block_duration_matches_times(self) -> None:
        for name, suggestion in MOCK_SCHEDULE_SUGGESTIONS.items():
            for block in suggestion["suggested_blocks"]:
                start_h, start_m = map(int, block["start_time"].split(":"))
                end_h, end_m = map(int, block["end_time"].split(":"))
                expected_hours = (end_h * 60 + end_m - start_h * 60 - start_m) / 60
                assert abs(block["duration_hours"] - expected_hours) < 0.01, (
                    f"Suggestion '{name}': duration mismatch "
                    f"({block['duration_hours']} vs {expected_hours})"
                )

    def test_suggestion_has_notes(self) -> None:
        for name, suggestion in MOCK_SCHEDULE_SUGGESTIONS.items():
            assert suggestion["notes"], (
                f"Suggestion '{name}' should have scheduling notes"
            )

    def test_mock_client_returns_suggestion(self) -> None:
        mock_client = MagicMock()
        suggestion = MOCK_SCHEDULE_SUGGESTIONS["simple_scheduling_request"]
        mock_client.generate.return_value = json.dumps(suggestion)
        mock_client.generate_json.return_value = suggestion
        result = mock_client.generate_json()
        assert "suggested_blocks" in result
        assert len(result["suggested_blocks"]) > 0

    def test_prompt_formatted_with_sample_data(self) -> None:
        sample = _get_sample("simple_scheduling_request")
        ctx = sample.schedule_context
        formatted = SCHEDULE_SUGGESTION_USER.format(
            task_description=ctx["task_description"],
            budget_hours=ctx["budget_hours"],
            deadline=ctx["deadline"],
            existing_events=ctx["existing_events"],
        )
        assert ctx["task_description"] in formatted
        assert str(ctx["budget_hours"]) in formatted
        assert ctx["deadline"] in formatted
