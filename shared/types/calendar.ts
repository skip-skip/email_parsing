export interface CalendarEvent {
  calendar_event_id: string;
  ticket_id: string;
  start_time: string;
  end_time: string;
  duration: number;
  status: string;
}

export interface ScheduleBlock {
  day: string;
  start_time: string;
  end_time: string;
  duration: number;
  calendar_event_id: string | null;
}
