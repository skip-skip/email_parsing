import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { api } from "@/services/api"
import type { ScheduleBlock } from "@/services/api"
import { ScheduleCard } from "@/components/ScheduleCard"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { AlertCircle, RefreshCw } from "lucide-react"
import { Button } from "@/components/ui/button"

export function SchedulingQueue() {
  const queryClient = useQueryClient()

  const {
    data: items,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ["scheduling-queue"],
    queryFn: async () => {
      const response = await api.scheduling.list()
      return response.data
    },
  })

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
    },
  })

  const declineMutation = useMutation({
    mutationFn: ({ ticketId, reason }: { ticketId: string; reason?: string }) =>
      api.scheduling.decline(ticketId, reason),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["scheduling-queue"] })
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
            <Card key={i} className="animate-pulse">
              <CardHeader>
                <div className="h-5 w-48 rounded bg-muted" />
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="h-4 w-32 rounded bg-muted" />
                <div className="h-4 w-64 rounded bg-muted" />
                <div className="h-24 w-full rounded bg-muted" />
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
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-destructive">
              <AlertCircle className="size-5" />
              Failed to load queue
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
        <h1 className="text-3xl font-bold tracking-tight">Scheduling Queue</h1>
        {items && items.length > 0 && (
          <span className="rounded-full bg-muted px-3 py-1 text-sm font-medium text-muted-foreground">
            {items.length} {items.length === 1 ? "item" : "items"}
          </span>
        )}
      </div>

      {items && items.length === 0 && (
        <Card>
          <CardHeader>
            <CardTitle>No items to schedule</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground">
              Tasks ready for scheduling will appear here.
            </p>
          </CardContent>
        </Card>
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
