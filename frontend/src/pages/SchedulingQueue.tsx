import { useEffect } from "react"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { api } from "@/services/api"
import type { ScheduleBlock } from "@/services/api"
import { ScheduleCard } from "@/components/ScheduleCard"
import { Card, CardContent } from "@/components/ui/card"
import { AlertCircle, RefreshCw, CalendarClock } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { EmptyState } from "@/components/EmptyState"
import { useToast } from "@/components/Toast"
import { useUIStore } from "@/stores/ui-store"

export function SchedulingQueue() {
  const queryClient = useQueryClient()
  const { toast } = useToast()
  const setLastUpdated = useUIStore((s) => s.setLastUpdated)

  const {
    data: items,
    isLoading,
    error,
    refetch,
    dataUpdatedAt,
  } = useQuery({
    queryKey: ["scheduling-queue"],
    queryFn: async () => {
      const response = await api.scheduling.list()
      return response.data
    },
    refetchInterval: 30_000,
  })

  useEffect(() => {
    if (dataUpdatedAt) {
      setLastUpdated("/scheduling")
    }
  }, [dataUpdatedAt, setLastUpdated])

  const approveMutation = useMutation({
    mutationFn: ({
      ticketId,
      blocks,
    }: {
      ticketId: string
      blocks?: ScheduleBlock[]
    }) => api.scheduling.approve(ticketId, blocks ? { selected_blocks: blocks } : undefined),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["scheduling-queue"] })
      toast("success", "Schedule accepted and calendar events created")
    },
    onError: () => {
      toast("error", "Failed to accept schedule. Please try again.")
    },
  })

  const declineMutation = useMutation({
    mutationFn: ({ ticketId, reason }: { ticketId: string; reason?: string }) =>
      api.scheduling.decline(ticketId, reason),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["scheduling-queue"] })
      toast("success", "Schedule declined and removed from queue")
    },
    onError: () => {
      toast("error", "Failed to decline schedule. Please try again.")
    },
  })

  const modifyMutation = useMutation({
    mutationFn: ({
      ticketId,
      blocks,
    }: {
      ticketId: string
      blocks: ScheduleBlock[]
    }) => api.scheduling.modify(ticketId, { blocks }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["scheduling-queue"] })
      toast("success", "Schedule modified successfully")
    },
    onError: () => {
      toast("error", "Failed to modify schedule. Please try again.")
    },
  })

  const isPending =
    approveMutation.isPending ||
    declineMutation.isPending ||
    modifyMutation.isPending

  if (isLoading) {
    return (
      <div className="space-y-6">
        <h1 className="text-3xl font-bold tracking-tight">Scheduling Queue</h1>
        <div className="space-y-4">
          {Array.from({ length: 3 }).map((_, i) => (
            <Card key={i}>
              <CardContent className="space-y-3 pt-6">
                <Skeleton className="h-5 w-48" />
                <Skeleton className="h-4 w-32" />
                <Skeleton className="h-4 w-64" />
                <Skeleton className="h-24 w-full" />
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
        <h1 className="text-3xl font-bold tracking-tight">Scheduling Queue</h1>
        <Card>
          <CardContent className="flex flex-col items-center gap-3 py-8">
            <AlertCircle className="size-8 text-destructive" />
            <p className="text-sm font-medium">Failed to load queue</p>
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
        <h1 className="text-3xl font-bold tracking-tight">Scheduling Queue</h1>
        <div className="flex items-center gap-3">
          {items && items.length > 0 && (
            <span className="rounded-full bg-muted px-3 py-1 text-sm font-medium text-muted-foreground">
              {items.length} {items.length === 1 ? "item" : "items"}
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

      {items && items.length === 0 && (
        <EmptyState
          icon={CalendarClock}
          title="No items to schedule"
          description="Tasks ready for scheduling will appear here. Once tasks have all required information, the system will suggest time blocks for your review."
        />
      )}

      {items && items.length > 0 && (
        <div className="space-y-4">
          {items.map((item) => (
            <ScheduleCard
              key={item.ticket_id}
              item={item}
              isPending={isPending}
              onApprove={(ticketId, blocks) =>
                approveMutation.mutate({ ticketId, blocks })
              }
              onDecline={(ticketId, reason) =>
                declineMutation.mutate({ ticketId, reason })
              }
              onModify={(ticketId, blocks) =>
                modifyMutation.mutate({ ticketId, blocks })
              }
            />
          ))}
        </div>
      )}
    </div>
  )
}
