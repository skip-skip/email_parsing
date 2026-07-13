from __future__ import annotations

from datetime import datetime, timedelta

from backend.app.services.validation.validator import TicketValidator


class TestTicketValidator:
    def setup_method(self) -> None:
        self.validator = TicketValidator()

    def test_complete_ticket_passes(self) -> None:
        data = {
            "task_description": "Redesign the company website with new branding",
            "project_number": "PRJ-2025-001",
            "budget_hours": 40,
            "deadline": (datetime.now() + timedelta(days=30)).isoformat(),
        }
        result = self.validator.validate(data)
        assert result.is_complete is True
        assert result.missing_fields == []

    def test_missing_task_description(self) -> None:
        data = {
            "project_number": "PRJ-2025-001",
            "budget_hours": 40,
            "deadline": "2025-12-31T00:00:00",
        }
        result = self.validator.validate(data)
        assert result.is_complete is False
        assert "task_description" in result.missing_fields

    def test_missing_project_number(self) -> None:
        data = {
            "task_description": "Redesign the company website with new branding",
            "budget_hours": 40,
            "deadline": "2025-12-31T00:00:00",
        }
        result = self.validator.validate(data)
        assert result.is_complete is False
        assert "project_number" in result.missing_fields

    def test_missing_budget_hours(self) -> None:
        data = {
            "task_description": "Redesign the company website with new branding",
            "project_number": "PRJ-2025-001",
            "deadline": "2025-12-31T00:00:00",
        }
        result = self.validator.validate(data)
        assert result.is_complete is False
        assert "budget_hours" in result.missing_fields

    def test_missing_deadline(self) -> None:
        data = {
            "task_description": "Redesign the company website with new branding",
            "project_number": "PRJ-2025-001",
            "budget_hours": 40,
        }
        result = self.validator.validate(data)
        assert result.is_complete is False
        assert "deadline" in result.missing_fields

    def test_empty_string_is_missing(self) -> None:
        data = {
            "task_description": "",
            "project_number": "PRJ-2025-001",
            "budget_hours": 40,
            "deadline": "2025-12-31T00:00:00",
        }
        result = self.validator.validate(data)
        assert result.is_complete is False
        assert "task_description" in result.missing_fields

    def test_zero_budget_hours_is_missing(self) -> None:
        data = {
            "task_description": "Redesign the company website with new branding",
            "project_number": "PRJ-2025-01",
            "budget_hours": 0,
            "deadline": "2025-12-31T00:00:00",
        }
        result = self.validator.validate(data)
        assert result.is_complete is False
        assert "budget_hours" in result.missing_fields

    def test_past_deadline_warning(self) -> None:
        data = {
            "task_description": "Redesign the company website with new branding",
            "project_number": "PRJ-2025-001",
            "budget_hours": 40,
            "deadline": "2020-01-01T00:00:00",
        }
        result = self.validator.validate(data)
        assert result.is_complete is True
        assert len(result.warnings) == 1
        assert "past" in result.warnings[0].lower()

    def test_field_status_populated(self) -> None:
        data = {
            "task_description": "Redesign the company website with new branding",
            "project_number": "PRJ-2025-001",
            "budget_hours": 40,
            "deadline": "2025-12-31T00:00:00",
        }
        result = self.validator.validate(data)
        assert all(result.field_status.values())

    def test_short_task_description_fails(self) -> None:
        data = {
            "task_description": "Short",
            "project_number": "PRJ-2025-001",
            "budget_hours": 40,
            "deadline": "2025-12-31T00:00:00",
        }
        result = self.validator.validate(data)
        assert result.is_complete is False
        assert "task_description" in result.missing_fields
