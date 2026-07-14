import { useEffect } from "react"
import { useQuery } from "@tanstack/react-query"
import { useNavigate } from "react-router-dom"
import { api } from "@/services/api"
import { TaskRow } from "@/components/TaskRow"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { EmptyState } from "@/components/EmptyState"
import { cn } from "@/lib/utils"
import { useUIStore } from "@/stores/ui-store"
import {
  AlertCircle,
  RefreshCw,
  Search,
  X,
  CheckCircle2,
} from "lucide-react"

const SORT_OPTIONS = [
  { value: "updated_at", label: "Updated" },
  { value: "created_at", label: "Created" },
  { value: "client", label: "Client" },
]

export function ClosedTasks() {
  const navigate = useNavigate()
  const setLastUpdated = useUIStore((s) => s.setLastUpdated)
  const closedClientFilter = useUIStore((s) => s.closedClientFilter)
  const setClosedClientFilter = useUIStore((s) => s.setClosedClientFilter)
  const closedSortField = useUIStore((s) => s.closedSortField)
  const closedSortDirection = useUIStore((s) => s.closedSortDirection)
  const setClosedSortField = useUIStore((s) => s.setClosedSortField)

  const effectiveSortField = closedSortField || "updated_at"

  const {
    data: ticketData,
    isLoading,
    error,
    refetch,
    dataUpdatedAt,
  } = useQuery({
    queryKey: ["closed-tasks", closedClientFilter, effectiveSortField, closedSortDirection],
    queryFn: async () => {
      const response = await api.tickets.closed({
        client: closedClientFilter || undefined,
        sort_by: effectiveSortField,
        sort_dir: closedSortDirection,
      })
      return response.data
    },
    refetchInterval: 30_000,
  })

  const tickets = ticketData?.items ?? []

  useEffect(() => {
    if (dataUpdatedAt) {
      setLastUpdated("/closed-tasks")
    }
  }, [dataUpdatedAt, setLastUpdated])

  function handleTaskClick(ticketId: string) {
    navigate(`/active-tasks/${ticketId}`)
  }

  if (isLoading) {
    return (
      <div className="space-y-6">
        <h1 className="text-3xl font-bold tracking-tight">Closed Tasks</h1>
        <div className="space-y-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <Card key={i}>
              <CardContent className="flex items-center gap-4 py-4">
                <div className="flex-1 space-y-2">
                  <Skeleton className="h-4 w-48" />
                  <Skeleton className="h-3 w-64" />
                </div>
                <Skeleton className="h-4 w-20" />
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
        <h1 className="text-3xl font-bold tracking-tight">Closed Tasks</h1>
        <Card>
          <CardContent className="flex flex-col items-center gap-3 py-8">
            <AlertCircle className="size-8 text-destructive" />
            <p className="text-sm font-medium">Failed to load closed tasks</p>
            <p className="text-center text-sm text-muted-foreground">
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
      <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <h1 className="text-3xl font-bold tracking-tight">Closed Tasks</h1>
        <div className="flex items-center gap-3">
          {tickets.length > 0 && (
            <span className="rounded-full bg-muted px-3 py-1 text-sm font-medium text-muted-foreground">
              {tickets.length} {tickets.length === 1 ? "task" : "tasks"}
            </span>
          )}
          <Button
            variant="ghost"
            size="sm"
            onClick={() => refetch()}
          >
            <RefreshCw className="size-3.5" />
            <span className="hidden sm:inline">Refresh</span>
          </Button>
        </div>
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <div className="relative">
          <Search className="absolute left-2.5 top-1/2 size-3.5 -translate-y-1/2 text-muted-foreground" />
          <input
            type="text"
            placeholder="Filter by client..."
            value={closedClientFilter}
            onChange={(e) => setClosedClientFilter(e.target.value)}
            className="h-7 rounded-full border bg-background pl-8 pr-7 text-xs outline-none focus:border-primary focus:ring-1 focus:ring-primary"
          />
          {closedClientFilter && (
            <button
              type="button"
              onClick={() => setClosedClientFilter("")}
              className="absolute right-1.5 top-1/2 -translate-y-1/2 rounded-full p-0.5 text-muted-foreground hover:text-foreground"
            >
              <X className="size-3" />
            </button>
          )}
        </div>

        <div className="flex flex-wrap items-center gap-1.5">
          {SORT_OPTIONS.map((opt) => (
            <button
              key={opt.value}
              type="button"
              onClick={() => setClosedSortField(opt.value)}
              className={cn(
                "rounded-full border px-2.5 py-0.5 text-xs font-medium transition-colors",
                effectiveSortField === opt.value
                  ? "border-primary bg-primary/10 text-primary"
                  : "border-transparent text-muted-foreground hover:text-foreground",
              )}
            >
              {opt.label}
              {effectiveSortField === opt.value && (
                <span className="ml-0.5">{closedSortDirection === "asc" ? "↑" : "↓"}</span>
              )}
            </button>
          ))}
        </div>
      </div>

      {tickets.length === 0 && (
        <EmptyState
          icon={CheckCircle2}
          title="No closed tasks"
          description="Completed, declined, or cancelled tasks will appear here."
        />
      )}

      {tickets.length > 0 && (
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
