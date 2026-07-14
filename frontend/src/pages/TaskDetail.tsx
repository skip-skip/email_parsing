import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { useParams, useNavigate } from "react-router-dom"
import { useState } from "react"
import { api, type ActiveTicket, type UpdateTicketRequest } from "@/services/api"
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { cn } from "@/lib/utils"
import {
  ArrowLeft,
  AlertCircle,
  RefreshCw,
  User,
  Mail,
  FolderOpen,
  Clock,
  CalendarClock,
  AlertTriangle,
  CheckCircle,
  Loader2,
  Hash,
  Timer,
  BarChart3,
  Pencil,
  Save,
  X,
} from "lucide-react"

function statusBadge(status: string): { label: string; className: string } {
  switch (status) {
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
        className: "text-muted-foreground bg-muted border-border",
      }
  }
}

function deadlineInfo(deadline: string | null): {
  text: string
  subtext: string
  className: string
  icon: typeof Clock
} {
  if (!deadline) {
    return {
      text: "No deadline set",
      subtext: "",
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
      text: `${Math.abs(diffDays)} days overdue`,
      subtext: `Deadline was ${deadlineDate.toLocaleDateString()}`,
      className: "text-red-600 dark:text-red-400",
      icon: AlertTriangle,
    }
  }
  if (diffDays === 0) {
    return {
      text: "Due today",
      subtext: deadlineDate.toLocaleTimeString(),
      className: "text-red-600 dark:text-red-400",
      icon: AlertTriangle,
    }
  }
  if (diffDays === 1) {
    return {
      text: "Due tomorrow",
      subtext: deadlineDate.toLocaleTimeString(),
      className: "text-amber-600 dark:text-amber-400",
      icon: Clock,
    }
  }
  return {
    text: `${diffDays} days remaining`,
    subtext: `Due ${deadlineDate.toLocaleDateString()}`,
    className: diffDays <= 7
      ? "text-amber-600 dark:text-amber-400"
      : "text-green-600 dark:text-green-400",
    icon: Clock,
  }
}

function InfoRow({
  icon: Icon,
  label,
  value,
}: {
  icon: typeof User
  label: string
  value: string | number | null
}) {
  return (
    <div className="flex items-start gap-3">
      <Icon className="mt-0.5 size-4 shrink-0 text-muted-foreground" />
      <div className="min-w-0">
        <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
          {label}
        </p>
        <p className="text-sm">
          {value ?? <span className="text-muted-foreground italic">Not set</span>}
        </p>
      </div>
    </div>
  )
}

function EditableField({
  icon: Icon,
  label,
  value,
  onChange,
  type = "text",
  min,
  max,
}: {
  icon: typeof User
  label: string
  value: string | number | null
  onChange: (value: string | number | null) => void
  type?: "text" | "number" | "datetime-local"
  min?: number
  max?: number
}) {
  const formatForInput = (v: string | number | null): string => {
    if (v === null) return ""
    if (type === "datetime-local" && typeof v === "string") {
      try {
        const date = new Date(v)
        return date.toISOString().slice(0, 16)
      } catch {
        return ""
      }
    }
    return String(v)
  }

  return (
    <div className="flex items-start gap-3">
      <Icon className="mt-0.5 size-4 shrink-0 text-muted-foreground" />
      <div className="min-w-0 flex-1">
        <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
          {label}
        </p>
        {type === "text" ? (
          <input
            type="text"
            value={formatForInput(value)}
            onChange={(e) => onChange(e.target.value || null)}
            className="mt-1 w-full rounded-md border bg-background px-3 py-1.5 text-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
          />
        ) : type === "number" ? (
          <input
            type="number"
            value={formatForInput(value)}
            onChange={(e) => onChange(e.target.value ? Number(e.target.value) : null)}
            min={min}
            max={max}
            className="mt-1 w-full rounded-md border bg-background px-3 py-1.5 text-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
          />
        ) : (
          <input
            type="datetime-local"
            value={formatForInput(value)}
            onChange={(e) => onChange(e.target.value ? e.target.value : null)}
            className="mt-1 w-full rounded-md border bg-background px-3 py-1.5 text-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
          />
        )}
      </div>
    </div>
  )
}

export function TaskDetail() {
  const { ticketId } = useParams<{ ticketId: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [isEditing, setIsEditing] = useState(false)
  const [editForm, setEditForm] = useState<UpdateTicketRequest>({})

  const {
    data: ticket,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ["active-task", ticketId],
    queryFn: async () => {
      const response = await api.tickets.get(ticketId!)
      return response.data
    },
    enabled: !!ticketId,
  })

  const updateMutation = useMutation({
    mutationFn: async (data: UpdateTicketRequest) => {
      const response = await api.tickets.update(ticketId!, data)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["active-task", ticketId] })
      queryClient.invalidateQueries({ queryKey: ["active-tasks"] })
      setIsEditing(false)
      setEditForm({})
    },
  })

  const handleStartEdit = () => {
    if (!ticket) return
    setEditForm({
      client: ticket.client,
      contact: ticket.contact,
      project_number: ticket.project_number,
      task_description: ticket.task_description,
      deadline: ticket.deadline,
      budget_hours: ticket.budget_hours,
      estimated_hours: ticket.estimated_hours,
      priority: ticket.priority,
    })
    setIsEditing(true)
  }

  const handleSaveEdit = () => {
    updateMutation.mutate(editForm)
  }

  const handleCancelEdit = () => {
    setIsEditing(false)
    setEditForm({})
  }

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center gap-4">
          <Skeleton className="size-7" />
          <Skeleton className="h-8 w-48" />
        </div>
        <div className="grid gap-4 md:grid-cols-2">
          <Card>
            <CardContent className="space-y-4 pt-6">
              <Skeleton className="h-4 w-32" />
              <Skeleton className="h-4 w-64" />
              <Skeleton className="h-4 w-48" />
            </CardContent>
          </Card>
          <Card>
            <CardContent className="space-y-4 pt-6">
              <Skeleton className="h-4 w-32" />
              <Skeleton className="h-4 w-64" />
              <Skeleton className="h-4 w-48" />
            </CardContent>
          </Card>
        </div>
        <Card>
          <CardContent className="pt-6">
            <Skeleton className="h-4 w-48 mb-3" />
            <Skeleton className="h-20 w-full" />
          </CardContent>
        </Card>
      </div>
    )
  }

  if (error || !ticket) {
    return (
      <div className="space-y-6">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => navigate("/active-tasks")}
        >
          <ArrowLeft className="size-3.5" />
          Back to Active Tasks
        </Button>
        <Card>
          <CardContent className="flex flex-col items-center gap-3 py-8">
            <AlertCircle className="size-8 text-destructive" />
            <p className="text-sm font-medium">Failed to load task</p>
            <p className="text-center text-sm text-muted-foreground">
              {error instanceof Error
                ? error.message
                : "Task not found."}
            </p>
            <Button variant="outline" size="sm" onClick={() => refetch()}>
              <RefreshCw className="size-3.5" />
              Retry
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  const badge = statusBadge(ticket.status)
  const deadline = deadlineInfo(isEditing ? editForm.deadline : ticket.deadline)
  const DeadlineIcon = deadline.icon
  const ticketIdShort = ticket.ticket_id.slice(0, 8)

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
        <Button
          variant="ghost"
          size="icon-sm"
          onClick={() => navigate("/active-tasks")}
        >
          <ArrowLeft className="size-4" />
        </Button>
        <div className="flex flex-wrap items-center gap-3">
          <h1 className="text-2xl font-bold tracking-tight sm:text-3xl">
            Ticket {ticketIdShort}...
          </h1>
          <div
            className={cn(
              "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium",
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
        <div className="ml-auto">
          {isEditing ? (
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={handleCancelEdit}
                disabled={updateMutation.isPending}
              >
                <X className="size-3.5" />
                Cancel
              </Button>
              <Button
                size="sm"
                onClick={handleSaveEdit}
                disabled={updateMutation.isPending}
              >
                {updateMutation.isPending ? (
                  <Loader2 className="size-3.5 animate-spin" />
                ) : (
                  <Save className="size-3.5" />
                )}
                Save
              </Button>
            </div>
          ) : (
            <Button
              variant="outline"
              size="sm"
              onClick={handleStartEdit}
            >
              <Pencil className="size-3.5" />
              Edit
            </Button>
          )}
        </div>
      </div>

      {updateMutation.isError && (
        <div className="rounded-md bg-red-50 p-3 text-sm text-red-800 dark:bg-red-950 dark:text-red-200">
          Failed to update ticket. Please try again.
        </div>
      )}

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <User className="size-4 text-muted-foreground" />
              Task Details
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {isEditing ? (
              <>
                <EditableField
                  icon={User}
                  label="Client"
                  value={editForm.client ?? null}
                  onChange={(v) => setEditForm({ ...editForm, client: v as string | null })}
                />
                <EditableField
                  icon={Mail}
                  label="Contact"
                  value={editForm.contact ?? null}
                  onChange={(v) => setEditForm({ ...editForm, contact: v as string | null })}
                />
                <EditableField
                  icon={FolderOpen}
                  label="Project Number"
                  value={editForm.project_number ?? null}
                  onChange={(v) => setEditForm({ ...editForm, project_number: v as string | null })}
                />
              </>
            ) : (
              <>
                <InfoRow icon={User} label="Client" value={ticket.client} />
                <InfoRow icon={Mail} label="Contact" value={ticket.contact} />
                <InfoRow icon={FolderOpen} label="Project Number" value={ticket.project_number} />
              </>
            )}
            <InfoRow icon={Hash} label="Ticket ID" value={ticket.ticket_id} />
            {ticket.conversation_id && (
              <InfoRow icon={Hash} label="Conversation ID" value={ticket.conversation_id} />
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="size-4 text-muted-foreground" />
              Time & Priority
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {isEditing ? (
              <>
                <EditableField
                  icon={Clock}
                  label="Deadline"
                  value={editForm.deadline ?? null}
                  onChange={(v) => setEditForm({ ...editForm, deadline: v as string | null })}
                  type="datetime-local"
                />
                <EditableField
                  icon={Timer}
                  label="Budget Hours"
                  value={editForm.budget_hours ?? null}
                  onChange={(v) => setEditForm({ ...editForm, budget_hours: v as number | null })}
                  type="number"
                  min={0}
                />
                <EditableField
                  icon={Timer}
                  label="Estimated Hours"
                  value={editForm.estimated_hours ?? null}
                  onChange={(v) => setEditForm({ ...editForm, estimated_hours: v as number | null })}
                  type="number"
                  min={0}
                />
                <EditableField
                  icon={BarChart3}
                  label="Priority"
                  value={editForm.priority ?? null}
                  onChange={(v) => setEditForm({ ...editForm, priority: v as number | null })}
                  type="number"
                  min={0}
                  max={10}
                />
              </>
            ) : (
              <>
                <div className="flex items-start gap-3">
                  <DeadlineIcon className={cn("mt-0.5 size-4 shrink-0", deadline.className)} />
                  <div className="min-w-0">
                    <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                      Deadline
                    </p>
                    <p className={cn("text-sm font-medium", deadline.className)}>
                      {deadline.text}
                    </p>
                    {deadline.subtext && (
                      <p className="text-xs text-muted-foreground">{deadline.subtext}</p>
                    )}
                  </div>
                </div>
                <InfoRow icon={Timer} label="Budget Hours" value={ticket.budget_hours} />
                <InfoRow icon={Timer} label="Estimated Hours" value={ticket.estimated_hours} />
                <InfoRow icon={BarChart3} label="Priority" value={ticket.priority} />
              </>
            )}
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Clock className="size-4 text-muted-foreground" />
            Task Description
          </CardTitle>
        </CardHeader>
        <CardContent>
          {isEditing ? (
            <textarea
              value={editForm.task_description ?? ""}
              onChange={(e) => setEditForm({ ...editForm, task_description: e.target.value || null })}
              rows={4}
              className="w-full rounded-md border bg-background px-3 py-2 text-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
            />
          ) : ticket.task_description ? (
            <p className="whitespace-pre-wrap text-sm leading-relaxed">
              {ticket.task_description}
            </p>
          ) : (
            <p className="text-sm italic text-muted-foreground">
              No description provided.
            </p>
          )}
        </CardContent>
      </Card>

      {ticket.calendar_events.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <CalendarClock className="size-4 text-muted-foreground" />
              Calendar Events
              <span className="rounded-full bg-muted px-2 py-0.5 text-xs font-medium text-muted-foreground">
                {ticket.calendar_events.length}
              </span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {ticket.calendar_events.map((event) => {
              const startDate = new Date(event.start_time)
              const endDate = new Date(event.end_time)
              return (
                <div
                  key={event.calendar_event_id}
                  className="flex items-center gap-4 rounded-lg border p-3"
                >
                  <CalendarClock className="size-4 shrink-0 text-purple-600 dark:text-purple-400" />
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-medium">
                      {startDate.toLocaleDateString()}{" "}
                      {startDate.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                      {" – "}
                      {endDate.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {event.duration}h · {event.status}
                    </p>
                  </div>
                </div>
              )
            })}
          </CardContent>
        </Card>
      )}

      <div className="flex flex-wrap items-center gap-4 text-xs text-muted-foreground">
        <span>Created: {new Date(ticket.created_at).toLocaleString()}</span>
        {ticket.updated_at && (
          <span>Updated: {new Date(ticket.updated_at).toLocaleString()}</span>
        )}
      </div>
    </div>
  )
}
