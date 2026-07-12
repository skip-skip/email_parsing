MISSING_INFO_DRAFT_VERSION = "v1.0.0"

MISSING_INFO_DRAFT_SYSTEM = """You are a professional email assistant. Draft a reply requesting missing information from the original sender.

The reply should:
- Be polite and professional
- Reference the original request
- Clearly list only the missing information needed
- Not repeat information already provided
- Keep the tone helpful and collaborative

Return the email body as plain text. Do not include a subject line."""

MISSING_INFO_DRAFT_USER = """Draft a reply to this email requesting missing information.

Original email:
From: {sender}
Subject: {subject}
Body: {body}

Information already provided:
- Client: {client}
- Task description: {task_description}
- Project number: {project_number}
- Deadline: {deadline}
- Budget hours: {budget_hours}

Missing information that needs to be requested:
{missing_fields}

Draft the reply email body:"""
