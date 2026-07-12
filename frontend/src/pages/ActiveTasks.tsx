import { useQuery } from "@tanstack/react-query"
import { useNavigate } from "react-router-dom"
import { api } from "@/services/api"
import { TaskRow } from "@/components/TaskRow"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import { useUIStore } from "@/stores/ui-store"
import { AlertCircle, RefreshCw, Search, X, ArrowUpDown } from "lucide-react"

const STATUS_OPTIONS = [
  { value: "", label: "All Active" },
  { value: "ACCEPTED", label: "Accepted" },
  { value: "CALENDAR_CREATED", label: "Scheduled" },
  { value: "IN_PROGRESS", label: "In Progress" },
]

const SORT_OPTIONS = [
  { value: "deadline", label: "Deadline" },
  { value: "created_at", label: "Created" },
  { value: "priority", label: "Priority" },
  { value: "client", label: "Client" },
]

export function ActiveTasks() {
  const navigate = useNavigate()
  const statusFilter = useUIStore((s) => s.activeTaskStatusFilter)
  const setStatusFilter = useUIStore((s) => s.setActiveTaskStatusFilter)
  const clientFilter = useUIStore((s) => s.activeTaskClientFilter)
  const setClientFilter = useUIStore((s) => s.setActiveTaskClientFilter)
  const sortField = useUIStore((s) => s.activeSortField)
  const sortDirection = useUIStore((s) => s.activeSortDirection)
  const setSortField = useUIStore((s) => s.setSortField)

  const effectiveSortField = sortField || "deadline"

  const {
    data: tickets,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ["active-tasks", statusFilter, clientFilter, effectiveSortField, sortDirection],
    queryFn: async () => {
      const response = await api.tickets.listActive({
        status: statusFilter || undefined,
        client: clientFilter || undefined,
        sort_by: effectiveSortField,
        sort_dir: sortDirection,
      })
      return response.data
    },
  })

  function handleTaskClick(ticketId: string) {
    navigate(`/active-tasks/${ticketId}`)
  }

  if (isLoading) {
    return (
      <div className="space-y-6">
        <h1 className="text-3xl font-bold tracking-tight">Active Tasks</h1>
        <div className="space-y-3">
          {Array.from({ length: 4 }).map((_, i) => (
            <Card key={i} className="animate-pulse">
              <CardContent className="flex items-center gap-4 py-4">
                <div className="flex-1 space-y-2">
                  <div className="h-4 w-48 rounded bg-muted" />
                  <div className="h-3 w-64 rounded bg-muted" />
                </div>
                <div className="h-4 w-20 rounded bg-muted" />
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="space-y-6">
        <h1 className="text-3xl font-bold tracking-tight">Active Tasks</h1>
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-destructive">
              <AlertCircle className="size-5" />
              Failed to load active tasks
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <p className="text-sm text-muted-foreground">
              {error instanceof Error
                ? error.message
                : "An unexpected error occurred."}
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

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold tracking-tight">Active Tasks</h1>
        {tickets && tickets.length > 0 && (
          <span className="rounded-full bg-muted px-3 py-1 text-sm font-medium text-muted-foreground">
            {tickets.length} {tickets.length === 1 ? "task" : "tasks"}
          </span>
        )}
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <div className="flex items-center gap-1.5">
          {STATUS_OPTIONS.map((opt) => (
            <button
              key={opt.value}
              type="button"
              onClick={() => setStatusFilter(opt.value)}
              className={cn(
                "rounded-full border px-3 py-1 text-xs font-medium transition-colors",
                statusFilter === opt.value
                  ? "border-primary bg-primary text-primary-foreground"
                  : "border-border bg-background text-muted-foreground hover:text-foreground",
              )}
            >
              {opt.label}
            </button>
          ))}
        </div>

        <div className="relative">
          <Search className="absolute left-2.5 top-1/2 size-3.5 -translate-y-1/2 text-muted-foreground" />
          <input
            type="text"
            placeholder="Filter by client..."
            value={clientFilter}
            onChange={(e) => setClientFilter(e.target.value)}
            className="h-7 rounded-full border bg-background pl-8 pr-7 text-xs outline-none focus:border-primary focus:ring-1 focus:ring-primary"
          />
          {clientFilter && (
            <button
              type="button"
              onClick={() => setClientFilter("")}
              className="absolute right-1.5 top-1/2 -translate-y-1/2 rounded-full p-0.5 text-muted-foreground hover:text-foreground"
            >
              <X className="size-3" />
            </button>
          )}
        </div>

        <div className="flex items-center gap-1.5">
          <ArrowUpDown className="size-3.5 text-muted-foreground" />
          {SORT_OPTIONS.map((opt) => (
            <button
              key={opt.value}
              type="button"
              onClick={() => setSortField(opt.value)}
              className={cn(
                "rounded-full border px-2.5 py-0.5 text-xs font-medium transition-colors",
                effectiveSortField === opt.value
                  ? "border-primary bg-primary/10 text-primary"
                  : "border-transparent text-muted-foreground hover:text-foreground",
              )}
            >
              {opt.label}
              {effectiveSortField === opt.value && (
                <span className="ml-0.5">{sortDirection === "asc" ? "↑" : "↓"}</span>
              )}
            </button>
          ))}
        </div>
      </div>

      {tickets && tickets.length === 0 && (
        <Card>
          <CardHeader>
            <CardTitle>No active tasks</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground">
              Accepted tasks with calendar events will appear here.
            </p>
          </CardContent>
        </Card>
      )}

      {tickets && tickets.length > 0 && (
        <div className="space-y-3">
          {tickets.map((ticket) => (
            <TaskRow
              key={ticket.ticket_id}
              ticket={ticket}
              onClick={handleTaskClick}
            />
          ))}
        </div>
      )}
    </div>
  )
}
