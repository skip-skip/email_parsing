from backend.app.workflows.states import TicketStatus


class InvalidTransitionError(Exception):
    def __init__(self, current: TicketStatus, target: TicketStatus) -> None:
        self.current = current
        self.target = target
        super().__init__(
            f"Invalid transition from {current.value} to {target.value}"
        )


VALID_TRANSITIONS: dict[TicketStatus, list[TicketStatus]] = {
    TicketStatus.NEW: [TicketStatus.PARSED, TicketStatus.WAITING_FOR_INFORMATION],
    TicketStatus.PARSED: [TicketStatus.VALIDATED, TicketStatus.WAITING_FOR_INFORMATION],
    TicketStatus.VALIDATED: [TicketStatus.READY_FOR_SCHEDULING, TicketStatus.WAITING_FOR_INFORMATION],
    TicketStatus.WAITING_FOR_INFORMATION: [TicketStatus.PARSED, TicketStatus.VALIDATED, TicketStatus.READY_FOR_SCHEDULING, TicketStatus.AWAITING_REPLY],
    TicketStatus.AWAITING_REPLY: [TicketStatus.READY_FOR_SCHEDULING, TicketStatus.WAITING_FOR_INFORMATION],
    TicketStatus.READY_FOR_SCHEDULING: [TicketStatus.PENDING_USER_APPROVAL],
    TicketStatus.PENDING_USER_APPROVAL: [TicketStatus.ACCEPTED, TicketStatus.WAITING_FOR_INFORMATION],
    TicketStatus.ACCEPTED: [TicketStatus.CALENDAR_CREATED],
    TicketStatus.CALENDAR_CREATED: [TicketStatus.IN_PROGRESS],
    TicketStatus.IN_PROGRESS: [TicketStatus.COMPLETED],
    TicketStatus.COMPLETED: [TicketStatus.ARCHIVED],
    TicketStatus.ARCHIVED: [],
    TicketStatus.DENIED: [],
}


def can_transition(current: TicketStatus, target: TicketStatus) -> bool:
    return target in VALID_TRANSITIONS.get(current, [])


def get_valid_transitions(current: TicketStatus) -> list[TicketStatus]:
    return VALID_TRANSITIONS.get(current, [])
