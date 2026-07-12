from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class EmailSample:
    name: str
    sender: str
    subject: str
    body: str
    received_time: str
    expected_extraction: dict
    missing_fields: list[str] = field(default_factory=list)
    schedule_context: dict = field(default_factory=dict)


EMAIL_SAMPLES: list[EmailSample] = [
    EmailSample(
        name="simple_scheduling_request",
        sender="alice.johnson@acmecorp.com",
        subject="Q3 Financial Report - PRJ-2025-012",
        body="""Hi team,

I need the Q3 financial report completed by July 25th. This should cover all revenue streams and expense categories.

Project: PRJ-2025-012
Client: Acme Corp
Estimated hours: 16

Please let me know if you need any additional data.

Best regards,
Alice Johnson""",
        received_time="2025-07-10T09:30:00",
        expected_extraction={
            "client": "Acme Corp",
            "sender": "alice.johnson@acmecorp.com",
            "subject": "Q3 Financial Report - PRJ-2025-012",
            "project_number": "PRJ-2025-012",
            "task_description": "Complete Q3 financial report covering all revenue streams and expense categories",
            "deadline": "2025-07-25T00:00:00",
            "budget_hours": 16,
            "attachments": [],
            "confidence": 0.95,
        },
        missing_fields=[],
        schedule_context={
            "task_description": "Complete Q3 financial report",
            "budget_hours": 16,
            "deadline": "2025-07-25",
            "existing_events": "Monday 10:00-11:00 Team standup; Wednesday 14:00-15:00 Client call",
        },
    ),
    EmailSample(
        name="missing_project_number",
        sender="bob.smith@globaltech.com",
        subject="Urgent: Website Redesign Needed",
        body="""Hello,

We need a complete redesign of our corporate website. The new site should be mobile-responsive and include a blog section.

Deadline: End of July 2025
Budget: approximately 40 hours

This is a high priority project. Please start as soon as possible.

Thanks,
Bob Smith
GlobalTech Inc""",
        received_time="2025-07-09T14:15:00",
        expected_extraction={
            "client": "GlobalTech Inc",
            "sender": "bob.smith@globaltech.com",
            "subject": "Urgent: Website Redesign Needed",
            "project_number": None,
            "task_description": "Complete redesign of corporate website, mobile-responsive with blog section",
            "deadline": "2025-07-31T00:00:00",
            "budget_hours": 40,
            "attachments": [],
            "confidence": 0.85,
        },
        missing_fields=["project_number"],
        schedule_context={
            "task_description": "Corporate website redesign",
            "budget_hours": 40,
            "deadline": "2025-07-31",
            "existing_events": "Tuesday 9:00-12:00 Development sprint; Thursday 13:00-16:00 Code review",
        },
    ),
    EmailSample(
        name="cancellation_request",
        sender="maria.garcia@startupxyz.io",
        subject="RE: Mobile App Development - PRJ-2025-008",
        body="""Hi,

Unfortunately, we need to cancel the mobile app development project (PRJ-2025-008). Due to budget constraints, we can no longer proceed with this initiative.

Please stop any ongoing work and let us know if there are any outstanding invoices.

Best,
Maria Garcia""",
        received_time="2025-07-08T11:00:00",
        expected_extraction={
            "client": "StartupXYZ",
            "sender": "maria.garcia@startupxyz.io",
            "subject": "RE: Mobile App Development - PRJ-2025-008",
            "project_number": "PRJ-2025-008",
            "task_description": "Cancel mobile app development project and stop ongoing work",
            "deadline": None,
            "budget_hours": None,
            "attachments": [],
            "confidence": 0.92,
        },
        missing_fields=[],
        schedule_context={},
    ),
    EmailSample(
        name="detailed_booking_with_attachments",
        sender="james.wilson@megacorp.com",
        subject="Data Migration Project - PRJ-2025-015",
        body="""Dear Team,

We are initiating a data migration project from our legacy Oracle database to PostgreSQL. Please find the detailed requirements document attached (requirements_v2.pdf).

Key requirements:
- Migrate 500GB of data
- Zero downtime during cutover
- Full data validation post-migration

Project Number: PRJ-2025-015
Deadline: August 15, 2025
Budget: 80 hours
Attachments: requirements_v2.pdf, schema_mapping.xlsx

Please review the attached documents and provide a timeline estimate.

Regards,
James Wilson
MegaCorp IT Director""",
        received_time="2025-07-07T08:45:00",
        expected_extraction={
            "client": "MegaCorp",
            "sender": "james.wilson@megacorp.com",
            "subject": "Data Migration Project - PRJ-2025-015",
            "project_number": "PRJ-2025-015",
            "task_description": "Data migration from legacy Oracle database to PostgreSQL, including 500GB migration with zero downtime and full data validation",
            "deadline": "2025-08-15T00:00:00",
            "budget_hours": 80,
            "attachments": ["requirements_v2.pdf", "schema_mapping.xlsx"],
            "confidence": 0.97,
        },
        missing_fields=[],
        schedule_context={
            "task_description": "Data migration Oracle to PostgreSQL",
            "budget_hours": 80,
            "deadline": "2025-08-15",
            "existing_events": "Monday 9:00-10:00 Standup; Wednesday 10:00-12:00 Architecture review; Friday 14:00-16:00 Sprint planning",
        },
    ),
    EmailSample(
        name="group_event_planning",
        sender="susan.lee@eventco.com",
        subject="Annual Company Retreat Planning - PRJ-2025-020",
        body="""Hi Everyone,

We need help planning our annual company retreat. Here are the details:

- 50 attendees
- 3-day event (September 12-14, 2025)
- Need venue booking, catering, and activity coordination
- Budget: $25,000
- Estimated planning hours: 60

This is for EventCo and should be tracked under PRJ-2025-020.

Please start with venue research.

Cheers,
Susan Lee""",
        received_time="2025-07-06T16:30:00",
        expected_extraction={
            "client": "EventCo",
            "sender": "susan.lee@eventco.com",
            "subject": "Annual Company Retreat Planning - PRJ-2025-020",
            "project_number": "PRJ-2025-020",
            "task_description": "Plan annual company retreat for 50 attendees, including venue booking, catering, and activity coordination",
            "deadline": "2025-09-12T00:00:00",
            "budget_hours": 60,
            "attachments": [],
            "confidence": 0.93,
        },
        missing_fields=[],
        schedule_context={
            "task_description": "Annual company retreat planning",
            "budget_hours": 60,
            "deadline": "2025-09-12",
            "existing_events": "None",
        },
    ),
    EmailSample(
        name="vague_request_missing_info",
        sender="tom.brown@vaguecorp.com",
        subject="Need some help",
        body="""Hey,

Can you help us with something? We have a project that needs attention but I don't have all the details right now.

Get back to me when you can.

Tom""",
        received_time="2025-07-05T13:20:00",
        expected_extraction={
            "client": "VagueCorp",
            "sender": "tom.brown@vaguecorp.com",
            "subject": "Need some help",
            "project_number": None,
            "task_description": None,
            "deadline": None,
            "budget_hours": None,
            "attachments": [],
            "confidence": 0.3,
        },
        missing_fields=["project_number", "task_description", "deadline", "budget_hours"],
        schedule_context={},
    ),
    EmailSample(
        name="multi_task_email",
        sender="patricia.nguyen@consulting.pro",
        subject="Multiple Deliverables - PRJ-2025-025",
        body="""Team,

We have several deliverables for the Henderson account:

1. UI/UX redesign - 20 hours
2. API integration - 15 hours
3. Performance audit - 10 hours

All must be completed by July 31, 2025. Project number is PRJ-2025-025.

Total budget: 45 hours

Please prioritize the UI/UX work first.

Patricia Nguyen""",
        received_time="2025-07-04T10:00:00",
        expected_extraction={
            "client": "Henderson",
            "sender": "patricia.nguyen@consulting.pro",
            "subject": "Multiple Deliverables - PRJ-2025-025",
            "project_number": "PRJ-2025-025",
            "task_description": "Multiple deliverables: UI/UX redesign, API integration, and performance audit",
            "deadline": "2025-07-31T00:00:00",
            "budget_hours": 45,
            "attachments": [],
            "confidence": 0.90,
        },
        missing_fields=[],
        schedule_context={
            "task_description": "UI/UX redesign, API integration, performance audit",
            "budget_hours": 45,
            "deadline": "2025-07-31",
            "existing_events": "Monday-Friday 9:00-17:00 already booked with other projects",
        },
    ),
    EmailSample(
        name="international_client",
        sender="hans.mueller@deutsche-tech.de",
        subject="ERP System Integration - PRJ-2025-030",
        body="""Sehr geehrte Damen und Herren,

We are seeking assistance with integrating our new ERP system with existing warehouse management software.

Project: PRJ-2025-030
Client: Deutsche Technik GmbH
Timeline: Must be completed by September 30, 2025
Budget: 120 hours

The integration involves:
- Real-time inventory sync
- Order processing automation
- Financial reporting bridge

Please provide a proposal at your earliest convenience.

Mit freundlichen Grüßen,
Hans Mueller
Deutsche Technik GmbH""",
        received_time="2025-07-03T07:00:00",
        expected_extraction={
            "client": "Deutsche Technik GmbH",
            "sender": "hans.mueller@deutsche-tech.de",
            "subject": "ERP System Integration - PRJ-2025-030",
            "project_number": "PRJ-2025-030",
            "task_description": "ERP system integration with warehouse management software, including real-time inventory sync, order processing automation, and financial reporting bridge",
            "deadline": "2025-09-30T00:00:00",
            "budget_hours": 120,
            "attachments": [],
            "confidence": 0.94,
        },
        missing_fields=[],
        schedule_context={
            "task_description": "ERP system integration",
            "budget_hours": 120,
            "deadline": "2025-09-30",
            "existing_events": "Tuesday 10:00-11:00 Status call; Thursday 9:00-10:00 Architecture review",
        },
    ),
    EmailSample(
        name="deadline_only_no_hours",
        sender="david.chen@financeplus.com",
        subject="Audit Preparation - PRJ-2025-035",
        body="""All,

Annual audit preparation is due August 1, 2025. We need to compile all financial records, create summary reports, and prepare supporting documentation.

Project: PRJ-2025-035
Client: FinancePlus

This is time-sensitive. Please prioritize.

David Chen""",
        received_time="2025-07-02T09:15:00",
        expected_extraction={
            "client": "FinancePlus",
            "sender": "david.chen@financeplus.com",
            "subject": "Audit Preparation - PRJ-2025-035",
            "project_number": "PRJ-2025-035",
            "task_description": "Annual audit preparation including compiling financial records, creating summary reports, and preparing supporting documentation",
            "deadline": "2025-08-01T00:00:00",
            "budget_hours": None,
            "attachments": [],
            "confidence": 0.88,
        },
        missing_fields=["budget_hours"],
        schedule_context={
            "task_description": "Annual audit preparation",
            "budget_hours": None,
            "deadline": "2025-08-01",
            "existing_events": "Wednesday 14:00-15:00 Finance review",
        },
    ),
    EmailSample(
        name="followup_with_new_info",
        sender="lisa.park@innovatelab.com",
        subject="RE: RE: Security Audit - PRJ-2025-018",
        body="""Hi,

Following up on our previous conversation. Here are the updated details:

- Updated project number: PRJ-2025-018
- Revised deadline: August 20, 2025
- Budget approved: 35 hours
- Scope: Full penetration testing and vulnerability assessment

We also need a written report delivered within 5 business days of the assessment.

Thanks,
Lisa Park""",
        received_time="2025-07-01T15:45:00",
        expected_extraction={
            "client": "InnovateLab",
            "sender": "lisa.park@innovatelab.com",
            "subject": "RE: RE: Security Audit - PRJ-2025-018",
            "project_number": "PRJ-2025-018",
            "task_description": "Full penetration testing and vulnerability assessment with written report within 5 business days",
            "deadline": "2025-08-20T00:00:00",
            "budget_hours": 35,
            "attachments": [],
            "confidence": 0.91,
        },
        missing_fields=[],
        schedule_context={
            "task_description": "Penetration testing and vulnerability assessment",
            "budget_hours": 35,
            "deadline": "2025-08-20",
            "existing_events": "Monday 13:00-14:00 Security review; Friday 9:00-11:00 Team meeting",
        },
    ),
    EmailSample(
        name="informal_chat_no_task",
        sender="mark.jones@bigbank.com",
        subject="Lunch next week?",
        body="""Hey,

Want to grab lunch next Tuesday? There's a new Thai place downtown I've been wanting to try.

Let me know!

Mark""",
        received_time="2025-06-30T12:00:00",
        expected_extraction={
            "client": None,
            "sender": "mark.jones@bigbank.com",
            "subject": "Lunch next week?",
            "project_number": None,
            "task_description": None,
            "deadline": None,
            "budget_hours": None,
            "attachments": [],
            "confidence": 0.1,
        },
        missing_fields=["client", "project_number", "task_description", "deadline", "budget_hours"],
        schedule_context={},
    ),
    EmailSample(
        name="urgent_with_partial_info",
        sender="karen.wright@retailco.com",
        subject="URGENT: Server Migration Tonight",
        body="""Team,

Emergency server migration needed tonight. Production server is failing and we need to migrate to the backup.

Client: RetailCo
Hours needed: 8
This cannot wait.

Karen""",
        received_time="2025-06-29T18:30:00",
        expected_extraction={
            "client": "RetailCo",
            "sender": "karen.wright@retailco.com",
            "subject": "URGENT: Server Migration Tonight",
            "project_number": None,
            "task_description": "Emergency server migration from failing production server to backup",
            "deadline": "2025-06-29T23:59:00",
            "budget_hours": 8,
            "attachments": [],
            "confidence": 0.82,
        },
        missing_fields=["project_number"],
        schedule_context={
            "task_description": "Emergency server migration",
            "budget_hours": 8,
            "deadline": "2025-06-29",
            "existing_events": "Today 19:00-21:00 Personal commitment",
        },
    ),
]

MOCK_LLM_EXTRACTION_RESPONSES: dict[str, dict] = {
    sample.name: sample.expected_extraction for sample in EMAIL_SAMPLES
}

MOCK_MISSING_INFO_DRAFTS: dict[str, str] = {
    "missing_project_number": """Dear Bob,

Thank you for reaching out regarding the website redesign project. We are excited about the opportunity to work with GlobalTech Inc on this initiative.

To ensure we can properly track and manage this project, could you please provide us with a project number or reference code? This helps us maintain accurate records and provide you with timely updates on progress.

If you don't have a project number assigned yet, please let us know and we can work with your preferred naming convention.

We look forward to hearing from you.

Best regards""",
    "vague_request_missing_info": """Dear Tom,

Thank you for reaching out. We would be happy to help with your project.

To get started, we need a few key details:

1. Project description - What specific work needs to be done?
2. Project number - Do you have a reference code for tracking?
3. Deadline - When does this need to be completed?
4. Budget hours - How many hours are allocated?

Once we have this information, we can begin planning and scheduling the work.

Best regards""",
    "deadline_only_no_hours": """Dear David,

Thank you for the audit preparation request. We understand this is time-sensitive and will prioritize accordingly.

To help us allocate the right resources and create an accurate timeline, could you please provide an estimated number of budgeted hours for this project? This will help us ensure we have adequate capacity to complete the work by August 1st.

We look forward to your response.

Best regards""",
}

MOCK_SCHEDULE_SUGGESTIONS: dict[str, dict] = {
    "simple_scheduling_request": {
        "suggested_blocks": [
            {"day": "Monday", "start_time": "09:00", "end_time": "12:00", "duration_hours": 3},
            {"day": "Wednesday", "start_time": "09:00", "end_time": "12:00", "duration_hours": 3},
            {"day": "Thursday", "start_time": "09:00", "end_time": "12:00", "duration_hours": 3},
            {"day": "Friday", "start_time": "09:00", "end_time": "12:00", "duration_hours": 3},
            {"day": "Monday", "start_time": "13:00", "end_time": "17:00", "duration_hours": 4},
        ],
        "total_scheduled_hours": 16,
        "notes": "All blocks scheduled before July 25 deadline. Morning blocks preferred.",
    },
    "detailed_booking_with_attachments": {
        "suggested_blocks": [
            {"day": "Monday", "start_time": "09:00", "end_time": "13:00", "duration_hours": 4},
            {"day": "Monday", "start_time": "14:00", "end_time": "17:00", "duration_hours": 3},
            {"day": "Tuesday", "start_time": "09:00", "end_time": "13:00", "duration_hours": 4},
            {"day": "Wednesday", "start_time": "09:00", "end_time": "13:00", "duration_hours": 4},
            {"day": "Wednesday", "start_time": "14:00", "end_time": "17:00", "duration_hours": 3},
            {"day": "Thursday", "start_time": "09:00", "end_time": "13:00", "duration_hours": 4},
            {"day": "Friday", "start_time": "09:00", "end_time": "13:00", "duration_hours": 4},
            {"day": "Monday", "start_time": "09:00", "end_time": "13:00", "duration_hours": 4},
            {"day": "Tuesday", "start_time": "09:00", "end_time": "13:00", "duration_hours": 4},
            {"day": "Wednesday", "start_time": "09:00", "end_time": "13:00", "duration_hours": 4},
            {"day": "Thursday", "start_time": "09:00", "end_time": "13:00", "duration_hours": 4},
            {"day": "Friday", "start_time": "09:00", "end_time": "13:00", "duration_hours": 4},
            {"day": "Monday", "start_time": "09:00", "end_time": "13:00", "duration_hours": 4},
            {"day": "Tuesday", "start_time": "09:00", "end_time": "13:00", "duration_hours": 4},
            {"day": "Wednesday", "start_time": "09:00", "end_time": "13:00", "duration_hours": 4},
            {"day": "Thursday", "start_time": "09:00", "end_time": "13:00", "duration_hours": 4},
            {"day": "Friday", "start_time": "09:00", "end_time": "13:00", "duration_hours": 4},
            {"day": "Monday", "start_time": "09:00", "end_time": "13:00", "duration_hours": 4},
            {"day": "Tuesday", "start_time": "09:00", "end_time": "13:00", "duration_hours": 4},
            {"day": "Wednesday", "start_time": "09:00", "end_time": "13:00", "duration_hours": 4},
        ],
        "total_scheduled_hours": 80,
        "notes": "Heavy schedule across 4 weeks. All blocks before Aug 15 deadline. Consider adding resources.",
    },
    "international_client": {
        "suggested_blocks": [
            {"day": "Monday", "start_time": "09:00", "end_time": "12:00", "duration_hours": 3},
            {"day": "Monday", "start_time": "13:00", "end_time": "17:00", "duration_hours": 4},
            {"day": "Wednesday", "start_time": "09:00", "end_time": "12:00", "duration_hours": 3},
            {"day": "Thursday", "start_time": "10:00", "end_time": "12:00", "duration_hours": 2},
            {"day": "Friday", "start_time": "09:00", "end_time": "12:00", "duration_hours": 3},
        ],
        "total_scheduled_hours": 15,
        "notes": "First week of ERP integration. More blocks needed in subsequent weeks to meet 120 hour budget.",
    },
}


@dataclass
class MissingInfoDraftTest:
    name: str
    sample_name: str
    expected_draft_keywords: list[str]
    expected_draft_forbidden: list[str] = field(default_factory=list)


MISSING_INFO_DRAFT_TESTS: list[MissingInfoDraftTest] = [
    MissingInfoDraftTest(
        name="draft_requests_project_number",
        sample_name="missing_project_number",
        expected_draft_keywords=["project number", "GlobalTech", "website redesign"],
        expected_draft_forbidden=["cancel", "refuse"],
    ),
    MissingInfoDraftTest(
        name="draft_requests_multiple_fields",
        sample_name="vague_request_missing_info",
        expected_draft_keywords=["project", "deadline", "hours", "description"],
        expected_draft_forbidden=[],
    ),
    MissingInfoDraftTest(
        name="draft_requests_budget_hours",
        sample_name="deadline_only_no_hours",
        expected_draft_keywords=["hours", "budget", "audit", "August"],
        expected_draft_forbidden=[],
    ),
]


@dataclass
class ScheduleSuggestionTest:
    name: str
    sample_name: str
    expected_min_blocks: int
    expected_total_hours: int
    max_deadline: str


SCHEDULE_SUGGESTION_TESTS: list[ScheduleSuggestionTest] = [
    ScheduleSuggestionTest(
        name="simple_16_hour_task",
        sample_name="simple_scheduling_request",
        expected_min_blocks=3,
        expected_total_hours=16,
        max_deadline="2025-07-25",
    ),
    ScheduleSuggestionTest(
        name="heavy_80_hour_task",
        sample_name="detailed_booking_with_attachments",
        expected_min_blocks=15,
        expected_total_hours=80,
        max_deadline="2025-08-15",
    ),
]
