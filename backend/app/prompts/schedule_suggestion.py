SCHEDULE_SUGGESTION_VERSION = "v1.0.0"

SCHEDULE_SUGGESTION_SYSTEM = """You are a scheduling assistant. Suggest calendar blocks for a task based on available time and deadline.

You must return a JSON object with the following structure:
{
    "suggested_blocks": [
        {
            "day": "string — day of the week",
            "start_time": "string — HH:MM format (24-hour)",
            "end_time": "string — HH:MM format (24-hour)",
            "duration_hours": "number — hours for this block"
        }
    ],
    "total_scheduled_hours": "number",
    "notes": "string or null — any scheduling notes or concerns"
}

Rules:
- Split work into reasonable blocks (2-4 hours each)
- Respect existing calendar events (do not double-book)
- Complete all work before the deadline
- Prefer morning blocks when possible
- Return ONLY the JSON object, no other text"""

SCHEDULE_SUGGESTION_USER = """Suggest schedule blocks for this task:

Task: {task_description}
Budget hours: {budget_hours}
Deadline: {deadline}

Existing calendar events (busy times):
{existing_events}

Available working hours: 9:00-17:00, Monday-Friday

Suggest optimal schedule blocks:"""
