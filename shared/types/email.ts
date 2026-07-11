export interface EmailMessage {
  email_id: string;
  conversation_id: string;
  entry_id: string;
  sender: string;
  subject: string;
  body: string;
  received_time: string;
  attachments: string[];
}

export interface ParsedEmail {
  client: string | null;
  sender: string;
  subject: string;
  project_number: string | null;
  task_description: string | null;
  deadline: string | null;
  budget_hours: number | null;
  attachments: string[];
  confidence: number;
}
