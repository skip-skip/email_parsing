import { useEffect, useState } from "react"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { api } from "@/services/api"
import { MissingInfoCard } from "@/components/MissingInfoCard"
import { Card, CardContent } from "@/components/ui/card"
import { AlertCircle, RefreshCw, Inbox, Clock, Send } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { EmptyState } from "@/components/EmptyState"
import { useToast } from "@/components/Toast"
import { useUIStore } from "@/stores/ui-store"
import { cn } from "@/lib/utils"

type TabId = "pending" | "awaiting"

export function MissingInfoQueue() {
  const queryClient = useQueryClient()
  const { toast } = useToast()
  const setLastUpdated = useUIStore((s) => s.setLastUpdated)
  const [activeTab, setActiveTab] = useState<TabId>("pending")

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

  const pendingItems = items?.filter((item) => item.status === "PENDING") ?? []
  const awaitingItems = items?.filter((item) => item.status === "AWAITING_REPLY") ?? []

  const tabs = [
    { id: "pending" as TabId, label: "Pending Review", count: pendingItems.length, icon: Inbox },
    { id: "awaiting" as TabId, label: "Awaiting Reply", count: awaitingItems.length, icon: Clock },
  ]

  const displayedItems = activeTab === "pending" ? pendingItems : awaitingItems

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

      <div className="flex gap-1 rounded-lg border bg-muted p-1">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            type="button"
            onClick={() => setActiveTab(tab.id)}
            className={cn(
              "flex items-center gap-2 rounded-md px-4 py-2 text-sm font-medium transition-colors",
              activeTab === tab.id
                ? "bg-background text-foreground shadow-sm"
                : "text-muted-foreground hover:text-foreground",
            )}
          >
            <tab.icon className="size-4" />
            {tab.label}
            {tab.count > 0 && (
              <span className="rounded-full bg-muted-foreground/20 px-2 py-0.5 text-xs font-medium">
                {tab.count}
              </span>
            )}
          </button>
        ))}
      </div>

      {displayedItems.length === 0 && (
        <EmptyState
          icon={activeTab === "pending" ? Inbox : Clock}
          title={activeTab === "pending" ? "No pending items" : "No awaiting reply items"}
          description={
            activeTab === "pending"
              ? "Tasks with missing information will appear here for review."
              : "Items awaiting a reply from the sender will appear here."
          }
        />
      )}

      {displayedItems.length > 0 && (
        <div className="space-y-4">
          {displayedItems.map((item) => (
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
