import apiClient from "./api-client"

export interface Ticket {
  ticket_id: string
  status: string
  client: string | null
  contact: string | null
  project_number: string | null
  task_description: string | null
  deadline: string | null
  budget_hours: number | null
  estimated_hours: number | null
  priority: number
  calendar_event_id: string | null
  conversation_id: string | null
  created_at: string
  updated_at: string | null
}

export interface DraftEmail {
  to: string
  subject: string
  body: string
  missing_fields: string[]
  ticket_id: string
}

export interface QueueItem {
  ticket_id: string
  draft_email: DraftEmail
  missing_fields: string[]
  created_at: string
  status: string
  confidence: number
  confidence_indicator: Record<string, string>
}

export interface ScheduleBlock {
  start_time: string
  end_time: string
  hours: number
  description: string
}

export interface ScheduleSuggestion {
  blocks: ScheduleBlock[]
  total_hours: number
  fits_deadline: boolean
  confidence: number
}

export interface SchedulingQueueItem {
  ticket_id: string
  suggestion: ScheduleSuggestion
  status: string
  created_at: string
  confidence: number
  confidence_indicator: Record<string, string>
}

export interface AILog {
  log_id: string
  ticket_id: string | null
  model: string
  prompt_version: string
  prompt: string
  response: string
  parsed_json: Record<string, unknown> | null
  confidence: number | null
  input_tokens: number | null
  output_tokens: number | null
  success: boolean
  error_message: string | null
  execution_time_ms: number | null
  created_at: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  offset: number
  limit: number
}

export interface AILogStats {
  total_interactions: number
  successful_interactions: number
  failed_interactions: number
  success_rate: number
  avg_execution_time_ms: number
  avg_confidence: number
  total_input_tokens: number
  total_output_tokens: number
  model_counts: Record<string, number>
}

export interface LLMHealth {
  status: string
  models: Record<
    string,
    {
      available: boolean
      last_checked: string | null
      last_error: string | null
    }
  >
  fallback_chain: string[]
  usage_stats: {
    total_requests: number
    successful_requests: number
    failed_requests: number
    model_counts: Record<string, number>
    model_switches: number
  }
}

export interface CalendarEvent {
  calendar_event_id: string
  outlook_event_id: string | null
  start_time: string
  end_time: string
  duration: number
  status: string
}

export interface ActiveTicket {
  ticket_id: string
  status: string
  client: string | null
  contact: string | null
  project_number: string | null
  task_description: string | null
  deadline: string | null
  budget_hours: number | null
  estimated_hours: number | null
  priority: number
  calendar_event_id: string | null
  conversation_id: string | null
  created_at: string
  updated_at: string | null
  calendar_events: CalendarEvent[]
}

export interface ApproveDraftRequest {
  edits?: {
    to: string
    subject: string
    body: string
    missing_fields: string[]
  }
}

export interface UpdateDraftRequest {
  to: string
  subject: string
  body: string
  missing_fields: string[]
}

export interface ApproveScheduleRequest {
  selected_blocks?: ScheduleBlock[]
}

export interface ModifyScheduleRequest {
  blocks: ScheduleBlock[]
}

export interface UpdateTicketRequest {
  client?: string | null
  contact?: string | null
  project_number?: string | null
  task_description?: string | null
  deadline?: string | null
  budget_hours?: number | null
  estimated_hours?: number | null
  priority?: number | null
}

export const api = {
  health: {
    check: () => apiClient.get<{ status: string }>("/health"),
  },

  missingInfo: {
    list: () => apiClient.get<QueueItem[]>("/api/queues/missing-info"),

    get: (ticketId: string) =>
      apiClient.get<QueueItem>(`/api/queues/missing-info/${ticketId}`),

    approve: (ticketId: string, data?: ApproveDraftRequest) =>
      apiClient.post<QueueItem>(
        `/api/queues/missing-info/${ticketId}/approve`,
        data,
      ),

    reject: (ticketId: string, reason?: string) =>
      apiClient.post<QueueItem>(
        `/api/queues/missing-info/${ticketId}/reject`,
        { reason },
      ),

    updateDraft: (ticketId: string, data: UpdateDraftRequest) =>
      apiClient.put<QueueItem>(
        `/api/queues/missing-info/${ticketId}/draft`,
        data,
      ),
  },

  scheduling: {
    list: () => apiClient.get<SchedulingQueueItem[]>("/api/scheduling/queue"),

    get: (ticketId: string) =>
      apiClient.get<SchedulingQueueItem>(
        `/api/scheduling/queue/${ticketId}`,
      ),

    approve: (ticketId: string, data?: ApproveScheduleRequest) =>
      apiClient.post<SchedulingQueueItem>(
        `/api/scheduling/queue/${ticketId}/approve`,
        data,
      ),

    decline: (ticketId: string, reason?: string) =>
      apiClient.post<SchedulingQueueItem>(
        `/api/scheduling/queue/${ticketId}/decline`,
        { reason },
      ),

    modify: (ticketId: string, data: ModifyScheduleRequest) =>
      apiClient.post<SchedulingQueueItem>(
        `/api/scheduling/queue/${ticketId}/modify`,
        data,
      ),
  },

  tickets: {
    listActive: (params?: {
      status?: string
      client?: string
      sort_by?: string
      sort_dir?: string
    }) => apiClient.get<PaginatedResponse<ActiveTicket>>("/api/tickets/active", { params }),

    get: (ticketId: string) =>
      apiClient.get<ActiveTicket>(`/api/tickets/${ticketId}`),

    update: (ticketId: string, data: UpdateTicketRequest) =>
      apiClient.patch<ActiveTicket>(`/api/tickets/${ticketId}`, data),

    close: (ticketId: string) =>
      apiClient.post<ActiveTicket>(`/api/tickets/${ticketId}/close`),

    closed: (params?: {
      client?: string
      sort_by?: string
      sort_dir?: string
      offset?: number
      limit?: number
    }) => apiClient.get<PaginatedResponse<ActiveTicket>>("/api/tickets/closed", { params }),
  },

  aiLogs: {
    list: (params?: {
      offset?: number
      limit?: number
      model?: string
      prompt_version?: string
      success?: boolean
      date_from?: string
      date_to?: string
    }) => apiClient.get<PaginatedResponse<AILog>>("/api/ai-logs", { params }),

    stats: () => apiClient.get<AILogStats>("/api/ai-logs/stats"),

    getByTicket: (ticketId: string) =>
      apiClient.get<AILog[]>(`/api/ai-logs/${ticketId}`),
  },

  llm: {
    health: () => apiClient.get<LLMHealth>("/api/llm/health"),
  },
}
