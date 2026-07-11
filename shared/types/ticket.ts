export const TicketStatus = {
  NEW: "NEW",
  PARSED: "PARSED",
  VALIDATED: "VALIDATED",
  WAITING_FOR_INFORMATION: "WAITING_FOR_INFORMATION",
  READY_FOR_SCHEDULING: "READY_FOR_SCHEDULING",
  PENDING_USER_APPROVAL: "PENDING_USER_APPROVAL",
  ACCEPTED: "ACCEPTED",
  CALENDAR_CREATED: "CALENDAR_CREATED",
  IN_PROGRESS: "IN_PROGRESS",
  COMPLETED: "COMPLETED",
  ARCHIVED: "ARCHIVED",
} as const;

export type TicketStatus =
  (typeof TicketStatus)[keyof typeof TicketStatus];

export interface TicketCreate {
  client: string;
  contact: string;
  project_number: string | null;
  task_description: string;
  deadline: string | null;
  budget_hours: number | null;
  estimated_hours: number | null;
  priority: number;
  conversation_id: string | null;
}

export interface TicketUpdate {
  status: TicketStatus | null;
  client: string | null;
  contact: string | null;
  project_number: string | null;
  task_description: string | null;
  deadline: string | null;
  budget_hours: number | null;
  estimated_hours: number | null;
  priority: number | null;
  calendar_event_id: string | null;
  conversation_id: string | null;
}

export interface TicketResponse {
  ticket_id: string;
  status: TicketStatus;
  client: string;
  contact: string;
  project_number: string | null;
  task_description: string;
  deadline: string | null;
  budget_hours: number | null;
  estimated_hours: number | null;
  priority: number;
  calendar_event_id: string | null;
  conversation_id: string | null;
  created_at: string;
  updated_at: string;
}
