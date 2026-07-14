import type { ActiveTicket } from "@/services/api"
import { Card, CardContent } from "@/components/ui/card"
import { cn } from "@/lib/utils"
import {
  CalendarClock,
  FolderOpen,
  User,
  Clock,
  AlertTriangle,
  CheckCircle,
  Loader2,
} from "lucide-react"

interface TaskRowProps {
  ticket: ActiveTicket
  onClick: (ticketId: string) => void
}

function statusBadge(status: string): { label: string; className: string } {
  switch (status) {
    case "NEW":
      return {
        label: "New",
        className:
          "text-gray-600 bg-gray-50 border-gray-200 dark:text-gray-400 dark:bg-gray-950 dark:border-gray-800",
      }
    case "WAITING_FOR_INFORMATION":
      return {
        label: "Waiting",
        className:
          "text-orange-600 bg-orange-50 border-orange-200 dark:text-orange-400 dark:bg-orange-950 dark:border-orange-800",
      }
    case "ACCEPTED":
      return {
        label: "Accepted",
        className:
          "text-blue-600 bg-blue-50 border-blue-200 dark:text-blue-400 dark:bg-blue-950 dark:border-blue-800",
      }
    case "CALENDAR_CREATED":
      return {
        label: "Scheduled",
        className:
          "text-purple-600 bg-purple-50 border-purple-200 dark:text-purple-400 dark:bg-purple-950 dark:border-purple-800",
      }
    case "IN_PROGRESS":
      return {
        label: "In Progress",
        className:
          "text-amber-600 bg-amber-50 border-amber-200 dark:text-amber-400 dark:bg-amber-950 dark:border-amber-800",
      }
    default:
      return {
        label: status,
        className:
          "text-muted-foreground bg-muted border-border",
      }
  }
}

function deadlineCountdown(deadline: string | null): {
  text: string
  className: string
  icon: typeof Clock
} {
  if (!deadline) {
    return {
      text: "No deadline",
      className: "text-muted-foreground",
      icon: Clock,
    }
  }

  const now = new Date()
  const deadlineDate = new Date(deadline)
  const diffMs = deadlineDate.getTime() - now.getTime()
  const diffDays = Math.ceil(diffMs / (1000 * 60 * 60 * 24))

  if (diffDays < 0) {
    return {
      text: `${Math.abs(diffDays)}d overdue`,
      className: "text-red-600 dark:text-red-400",
      icon: AlertTriangle,
    }
  }
  if (diffDays === 0) {
    return {
      text: "Due today",
      className: "text-red-600 dark:text-red-400",
      icon: AlertTriangle,
    }
  }
  if (diffDays === 1) {
    return {
      text: "Due tomorrow",
      className: "text-amber-600 dark:text-amber-400",
      icon: Clock,
    }
  }
  if (diffDays <= 7) {
    return {
      text: `${diffDays} days left`,
      className: "text-amber-600 dark:text-amber-400",
      icon: Clock,
    }
  }
  return {
    text: `${diffDays} days left`,
    className: "text-green-600 dark:text-green-400",
    icon: Clock,
  }
}

export function TaskRow({ ticket, onClick }: TaskRowProps) {
  const badge = statusBadge(ticket.status)
  const countdown = deadlineCountdown(ticket.deadline)
  const CountdownIcon = countdown.icon
  const ticketIdShort = ticket.ticket_id.slice(0, 8)

  const hasCalendarEvents = ticket.calendar_events.length > 0

  return (
    <Card
      className="cursor-pointer transition-colors hover:bg-muted/50"
      onClick={() => onClick(ticket.ticket_id)}
    >
      <CardContent className="flex items-center gap-4">
        <div className="flex min-w-0 flex-1 items-center gap-4">
          <div className="min-w-0 flex-1 space-y-1">
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium">Ticket {ticketIdShort}...</span>
              <div
                className={cn(
                  "inline-flex items-center rounded-full border px-2 py-0.5 text-xs font-medium",
                  badge.className,
                )}
              >
                {ticket.status === "IN_PROGRESS" && (
                  <Loader2 className="mr-1 size-3 animate-spin" />
                )}
                {ticket.status === "CALENDAR_CREATED" && (
                  <CalendarClock className="mr-1 size-3" />
                )}
                {ticket.status === "ACCEPTED" && (
                  <CheckCircle className="mr-1 size-3" />
                )}
                {badge.label}
              </div>
            </div>
            <div className="flex items-center gap-3 text-xs text-muted-foreground">
              {ticket.client && (
                <span className="flex items-center gap-1">
                  <User className="size-3" />
                  {ticket.client}
                </span>
              )}
              {ticket.project_number && (
                <span className="flex items-center gap-1">
                  <FolderOpen className="size-3" />
                  {ticket.project_number}
                </span>
              )}
              {ticket.task_description && (
                <span className="truncate">
                  {ticket.task_description}
                </span>
              )}
            </div>
          </div>

          <div className="flex items-center gap-4 text-xs">
            {hasCalendarEvents && (
              <span className="flex items-center gap-1 text-purple-600 dark:text-purple-400">
                <CalendarClock className="size-3" />
                {ticket.calendar_events.length} event{ticket.calendar_events.length !== 1 ? "s" : ""}
              </span>
            )}
            <span className={cn("flex items-center gap-1 font-medium", countdown.className)}>
              <CountdownIcon className="size-3" />
              {countdown.text}
            </span>
            {ticket.deadline && (
              <span className="text-muted-foreground">
                {new Date(ticket.deadline).toLocaleDateString()}
              </span>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
