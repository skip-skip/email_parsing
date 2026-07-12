import { useEffect } from "react"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { api } from "@/services/api"
import { MissingInfoCard } from "@/components/MissingInfoCard"
import { Card, CardContent } from "@/components/ui/card"
import { AlertCircle, RefreshCw, Inbox } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { EmptyState } from "@/components/EmptyState"
import { useToast } from "@/components/Toast"
import { useUIStore } from "@/stores/ui-store"

export function MissingInfoQueue() {
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
    queryKey: ["missing-info-queue"],
    queryFn: async () => {
      const response = await api.missingInfo.list()
      return response.data
    },
    refetchInterval: 30_000,
  })

  useEffect(() => {
    if (dataUpdatedAt) {
      setLastUpdated("/missing-info")
    }
  }, [dataUpdatedAt, setLastUpdated])

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
      toast("success", "Draft approved and sent successfully")
    },
    onError: () => {
      toast("error", "Failed to approve draft. Please try again.")
    },
  })

  const rejectMutation = useMutation({
    mutationFn: ({ ticketId, reason }: { ticketId: string; reason?: string }) =>
      api.missingInfo.reject(ticketId, reason),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["missing-info-queue"] })
      toast("success", "Draft rejected and removed from queue")
    },
    onError: () => {
      toast("error", "Failed to reject draft. Please try again.")
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
      toast("success", "Draft updated successfully")
    },
    onError: () => {
      toast("error", "Failed to update draft. Please try again.")
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
            <Card key={i}>
              <CardContent className="space-y-3 pt-6">
                <Skeleton className="h-5 w-48" />
                <Skeleton className="h-4 w-32" />
                <Skeleton className="h-4 w-64" />
                <Skeleton className="h-20 w-full" />
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
        <h1 className="text-3xl font-bold tracking-tight">
          Missing Information Queue
        </h1>
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
          icon={Inbox}
          title="No items in queue"
          description="Tasks with missing information will appear here for review. When the system detects incomplete task data, it will draft a follow-up email for your approval."
        />
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
