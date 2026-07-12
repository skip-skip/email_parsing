MISSING_INFO_DRAFT_VERSION = "v1.0.0"

MISSING_INFO_DRAFT_SYSTEM = """You are a professional email assistant. Draft a polite email requesting missing information from a client.

Rules:
- Be professional and courteous
- Clearly list the specific information needed
- Explain why the information is needed
- Provide a deadline for response if appropriate
- Keep the email concise but complete
- Use a friendly but business-appropriate tone"""

MISSING_INFO_DRAFT_USER = """Draft a reply to the following email requesting missing information:

Original Email:
From: {sender}
Subject: {subject}

Missing Information:
{missing_fields_list}

Ticket Context:
- Client: {client}
- Project: {project_number}
- Task: {task_description}

Please draft a professional email requesting the missing information above."""
