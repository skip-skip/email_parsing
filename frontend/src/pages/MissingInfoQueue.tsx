import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { api } from "@/services/api"
import { MissingInfoCard } from "@/components/MissingInfoCard"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { AlertCircle, RefreshCw } from "lucide-react"
import { Button } from "@/components/ui/button"

export function MissingInfoQueue() {
  const queryClient = useQueryClient()

  const {
    data: items,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ["missing-info-queue"],
    queryFn: async () => {
      const response = await api.missingInfo.list()
      return response.data
    },
  })

  const approveMutation = useMutation({
    mutationFn: ({
      ticketId,
      edits,
    }: {
      ticketId: string
      edits?: Parameters<typeof api.missingInfo.approve>[1]
    }) => api.missingInfo.approve(ticketId, edits),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["missing-info-queue"] })
    },
  })

  const rejectMutation = useMutation({
    mutationFn: ({ ticketId, reason }: { ticketId: string; reason?: string }) =>
      api.missingInfo.reject(ticketId, reason),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["missing-info-queue"] })
    },
  })

  const updateDraftMutation = useMutation({
    mutationFn: ({
      ticketId,
      draft,
    }: {
      ticketId: string
      draft: Parameters<typeof api.missingInfo.updateDraft>[1]
    }) => api.missingInfo.updateDraft(ticketId, draft),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["missing-info-queue"] })
    },
  })

  const isPending =
    approveMutation.isPending ||
    rejectMutation.isPending ||
    updateDraftMutation.isPending

  if (isLoading) {
    return (
      <div className="space-y-6">
        <h1 className="text-3xl font-bold tracking-tight">
          Missing Information Queue
        </h1>
        <div className="space-y-4">
          {Array.from({ length: 3 }).map((_, i) => (
            <Card key={i} className="animate-pulse">
              <CardHeader>
                <div className="h-5 w-48 rounded bg-muted" />
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="h-4 w-32 rounded bg-muted" />
                <div className="h-4 w-64 rounded bg-muted" />
                <div className="h-20 w-full rounded bg-muted" />
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
        <h1 className="text-3xl font-bold tracking-tight">
          Missing Information Queue
        </h1>
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
        <h1 className="text-3xl font-bold tracking-tight">
          Missing Information Queue
        </h1>
        {items && items.length > 0 && (
          <span className="rounded-full bg-muted px-3 py-1 text-sm font-medium text-muted-foreground">
            {items.length} {items.length === 1 ? "item" : "items"}
          </span>
        )}
      </div>

      {items && items.length === 0 && (
        <Card>
          <CardHeader>
            <CardTitle>No items in queue</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground">
              Tasks with missing information will appear here for review.
            </p>
          </CardContent>
        </Card>
      )}

      {items && items.length > 0 && (
        <div className="space-y-4">
          {items.map((item) => (
            <MissingInfoCard
              key={item.ticket_id}
              item={item}
              isPending={isPending}
              onApprove={(ticketId) => approveMutation.mutate({ ticketId })}
              onReject={(ticketId, reason) =>
                rejectMutation.mutate({ ticketId, reason })
              }
              onUpdateDraft={(ticketId, draft) =>
                updateDraftMutation.mutate({ ticketId, draft })
              }
            />
          ))}
        </div>
      )}
    </div>
  )
}
