from __future__ import annotations

import pytest

from backend.app.workflows.states import TicketStatus
from backend.app.workflows.transitions import (
    InvalidTransitionError,
    VALID_TRANSITIONS,
    can_transition,
    get_valid_transitions,
)


class TestTransitions:
    def test_can_transition_valid(self) -> None:
        assert can_transition(TicketStatus.NEW, TicketStatus.PARSED) is True
        assert can_transition(TicketStatus.PARSED, TicketStatus.VALIDATED) is True
        assert can_transition(TicketStatus.VALIDATED, TicketStatus.READY_FOR_SCHEDULING) is True

    def test_can_transition_invalid(self) -> None:
        assert can_transition(TicketStatus.NEW, TicketStatus.COMPLETED) is False
        assert can_transition(TicketStatus.ARCHIVED, TicketStatus.NEW) is False

    def test_get_valid_transitions_new(self) -> None:
        transitions = get_valid_transitions(TicketStatus.NEW)
        assert TicketStatus.PARSED in transitions
        assert TicketStatus.WAITING_FOR_INFORMATION in transitions

    def test_get_valid_transitions_archived(self) -> None:
        transitions = get_valid_transitions(TicketStatus.ARCHIVED)
        assert transitions == []

    def test_all_statuses_have_transitions_defined(self) -> None:
        for status in TicketStatus:
            assert status in VALID_TRANSITIONS

    def test_invalid_transition_error_message(self) -> None:
        with pytest.raises(InvalidTransitionError) as exc_info:
            raise InvalidTransitionError(TicketStatus.NEW, TicketStatus.COMPLETED)
        assert "NEW" in str(exc_info.value)
        assert "COMPLETED" in str(exc_info.value)
