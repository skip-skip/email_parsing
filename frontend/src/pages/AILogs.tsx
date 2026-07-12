import { useState, useEffect } from "react"
import { useQuery } from "@tanstack/react-query"
import { api } from "@/services/api"
import type { AILog, PaginatedResponse, AILogStats } from "@/services/api"
import { LogDetail } from "@/components/LogDetail"
import {
  Card,
  CardContent,
} from "@/components/ui/card"
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
  ChevronLeft,
  ChevronRight,
  ChevronDown,
  ChevronRight as ChevronRightIcon,
  CheckCircle,
  XCircle,
  Clock,
  BarChart3,
  Zap,
  ScrollText,
} from "lucide-react"

const PAGE_SIZE = 25

const STATUS_OPTIONS = [
  { value: "", label: "All" },
  { value: "true", label: "Success" },
  { value: "false", label: "Failed" },
]

export function AILogs() {
  const [offset, setOffset] = useState(0)
  const [searchText, setSearchText] = useState("")
  const [modelFilter, setModelFilter] = useState("")
  const [promptVersionFilter, setPromptVersionFilter] = useState("")
  const [successFilter, setSuccessFilter] = useState("")
  const [expandedLogId, setExpandedLogId] = useState<string | null>(null)
  const setLastUpdated = useUIStore((s) => s.setLastUpdated)

  const successValue =
    successFilter === "" ? undefined : successFilter === "true"

  const {
    data: logsData,
    isLoading,
    error,
    refetch,
    dataUpdatedAt,
  } = useQuery({
    queryKey: [
      "ai-logs",
      offset,
      modelFilter,
      promptVersionFilter,
      successFilter,
    ],
    queryFn: async () => {
      const response = await api.aiLogs.list({
        offset,
        limit: PAGE_SIZE,
        model: modelFilter || undefined,
        prompt_version: promptVersionFilter || undefined,
        success: successValue,
      })
      return response.data
    },
    refetchInterval: 60_000,
  })

  useEffect(() => {
    if (dataUpdatedAt) {
      setLastUpdated("/ai-logs")
    }
  }, [dataUpdatedAt, setLastUpdated])

  const { data: stats } = useQuery({
    queryKey: ["ai-logs-stats"],
    queryFn: async () => {
      const response = await api.aiLogs.stats()
      return response.data
    },
  })

  const totalPages = logsData
    ? Math.ceil(logsData.total / PAGE_SIZE)
    : 0
  const currentPage = logsData ? Math.floor(logsData.offset / PAGE_SIZE) + 1 : 1

  const filteredLogs = useFilterLogs(logsData, searchText)

  function toggleExpand(logId: string) {
    setExpandedLogId((prev) => (prev === logId ? null : logId))
  }

  if (isLoading) {
    return (
      <div className="space-y-6">
        <h1 className="text-3xl font-bold tracking-tight">AI Logs</h1>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Card key={i}>
              <CardContent className="flex items-center gap-3 py-3">
                <Skeleton className="size-8 rounded-lg" />
                <div className="space-y-1.5">
                  <Skeleton className="h-3 w-20" />
                  <Skeleton className="h-5 w-12" />
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
        <div className="space-y-3">
          {Array.from({ length: 4 }).map((_, i) => (
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
        <h1 className="text-3xl font-bold tracking-tight">AI Logs</h1>
        <Card>
          <CardContent className="flex flex-col items-center gap-3 py-8">
            <AlertCircle className="size-8 text-destructive" />
            <p className="text-sm font-medium">Failed to load AI logs</p>
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
        <h1 className="text-3xl font-bold tracking-tight">AI Logs</h1>
        <div className="flex items-center gap-3">
          {logsData && logsData.total > 0 && (
            <span className="rounded-full bg-muted px-3 py-1 text-sm font-medium text-muted-foreground">
              {logsData.total} {logsData.total === 1 ? "log" : "logs"}
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

      {stats && <StatsBar stats={stats} />}

      <div className="flex flex-wrap items-center gap-3">
        <div className="relative">
          <Search className="absolute left-2.5 top-1/2 size-3.5 -translate-y-1/2 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search logs..."
            value={searchText}
            onChange={(e) => {
              setSearchText(e.target.value)
              setOffset(0)
            }}
            className="h-7 rounded-full border bg-background pl-8 pr-7 text-xs outline-none focus:border-primary focus:ring-1 focus:ring-primary"
          />
          {searchText && (
            <button
              type="button"
              onClick={() => setSearchText("")}
              className="absolute right-1.5 top-1/2 -translate-y-1/2 rounded-full p-0.5 text-muted-foreground hover:text-foreground"
            >
              <X className="size-3" />
            </button>
          )}
        </div>

        <input
          type="text"
          placeholder="Model..."
          value={modelFilter}
          onChange={(e) => {
            setModelFilter(e.target.value)
            setOffset(0)
          }}
          className="h-7 rounded-full border bg-background px-3 text-xs outline-none focus:border-primary focus:ring-1 focus:ring-primary"
        />

        <input
          type="text"
          placeholder="Prompt version..."
          value={promptVersionFilter}
          onChange={(e) => {
            setPromptVersionFilter(e.target.value)
            setOffset(0)
          }}
          className="h-7 rounded-full border bg-background px-3 text-xs outline-none focus:border-primary focus:ring-1 focus:ring-primary"
        />

        <div className="flex flex-wrap items-center gap-1.5">
          {STATUS_OPTIONS.map((opt) => (
            <button
              key={opt.value}
              type="button"
              onClick={() => {
                setSuccessFilter(opt.value)
                setOffset(0)
              }}
              className={cn(
                "rounded-full border px-3 py-1 text-xs font-medium transition-colors",
                successFilter === opt.value
                  ? "border-primary bg-primary text-primary-foreground"
                  : "border-border bg-background text-muted-foreground hover:text-foreground",
              )}
            >
              {opt.label}
            </button>
          ))}
        </div>

        {(searchText || modelFilter || promptVersionFilter || successFilter) && (
          <Button
            variant="ghost"
            size="sm"
            onClick={() => {
              setSearchText("")
              setModelFilter("")
              setPromptVersionFilter("")
              setSuccessFilter("")
              setOffset(0)
            }}
          >
            <X className="size-3" />
            Clear filters
          </Button>
        )}
      </div>

      {logsData && logsData.items.length === 0 && (
        <EmptyState
          icon={ScrollText}
          title="No logs found"
          description={
            logsData.total === 0
              ? "AI interaction logs will appear here as the system processes emails."
              : "No logs match the current filters. Try adjusting your search criteria."
          }
        />
      )}

      {logsData && logsData.items.length > 0 && (
        <div className="space-y-2">
          {filteredLogs.map((log) => (
            <LogRow
              key={log.log_id}
              log={log}
              isExpanded={expandedLogId === log.log_id}
              onToggle={() => toggleExpand(log.log_id)}
            />
          ))}
        </div>
      )}

      {logsData && logsData.total > PAGE_SIZE && (
        <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
          <p className="text-xs text-muted-foreground">
            Showing {logsData.offset + 1}–
            {Math.min(logsData.offset + PAGE_SIZE, logsData.total)} of{" "}
            {logsData.total}
          </p>
          <div className="flex items-center gap-1">
            <Button
              variant="outline"
              size="sm"
              disabled={offset === 0}
              onClick={() => setOffset(Math.max(0, offset - PAGE_SIZE))}
            >
              <ChevronLeft className="size-3.5" />
              Previous
            </Button>
            <span className="px-3 text-xs text-muted-foreground">
              Page {currentPage} of {totalPages}
            </span>
            <Button
              variant="outline"
              size="sm"
              disabled={offset + PAGE_SIZE >= logsData.total}
              onClick={() => setOffset(offset + PAGE_SIZE)}
            >
              Next
              <ChevronRight className="size-3.5" />
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}

function StatsBar({ stats }: { stats: AILogStats }) {
  return (
    <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
      <Card size="sm">
        <CardContent className="flex items-center gap-3 py-3">
          <div className="rounded-lg bg-blue-100 p-2 dark:bg-blue-900/30">
            <BarChart3 className="size-4 text-blue-600 dark:text-blue-400" />
          </div>
          <div>
            <p className="text-xs text-muted-foreground">Total Interactions</p>
            <p className="text-lg font-semibold">{stats.total_interactions}</p>
          </div>
        </CardContent>
      </Card>
      <Card size="sm">
        <CardContent className="flex items-center gap-3 py-3">
          <div className="rounded-lg bg-green-100 p-2 dark:bg-green-900/30">
            <CheckCircle className="size-4 text-green-600 dark:text-green-400" />
          </div>
          <div>
            <p className="text-xs text-muted-foreground">Success Rate</p>
            <p className="text-lg font-semibold">
              {(stats.success_rate * 100).toFixed(1)}%
            </p>
          </div>
        </CardContent>
      </Card>
      <Card size="sm">
        <CardContent className="flex items-center gap-3 py-3">
          <div className="rounded-lg bg-amber-100 p-2 dark:bg-amber-900/30">
            <Clock className="size-4 text-amber-600 dark:text-amber-400" />
          </div>
          <div>
            <p className="text-xs text-muted-foreground">Avg Execution</p>
            <p className="text-lg font-semibold">
              {Math.round(stats.avg_execution_time_ms)}ms
            </p>
          </div>
        </CardContent>
      </Card>
      <Card size="sm">
        <CardContent className="flex items-center gap-3 py-3">
          <div className="rounded-lg bg-purple-100 p-2 dark:bg-purple-900/30">
            <Zap className="size-4 text-purple-600 dark:text-purple-400" />
          </div>
          <div>
            <p className="text-xs text-muted-foreground">Total Tokens</p>
            <p className="text-lg font-semibold">
              {(stats.total_input_tokens + stats.total_output_tokens).toLocaleString()}
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

function LogRow({
  log,
  isExpanded,
  onToggle,
}: {
  log: AILog
  isExpanded: boolean
  onToggle: () => void
}) {
  const createdDate = new Date(log.created_at)

  return (
    <div className="rounded-lg border bg-card">
      <button
        type="button"
        onClick={onToggle}
        className="flex w-full items-center gap-3 px-4 py-3 text-left transition-colors hover:bg-muted/50"
      >
        <div className="shrink-0">
          {isExpanded ? (
            <ChevronDown className="size-4 text-muted-foreground" />
          ) : (
            <ChevronRightIcon className="size-4 text-muted-foreground" />
          )}
        </div>

        <div className="flex items-center gap-1.5">
          {log.success ? (
            <CheckCircle className="size-3.5 text-green-600 dark:text-green-400" />
          ) : (
            <XCircle className="size-3.5 text-red-600 dark:text-red-400" />
          )}
        </div>

        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <span className="truncate text-sm font-medium">{log.model}</span>
            <span className="shrink-0 rounded bg-muted px-1.5 py-0.5 text-[10px] font-mono text-muted-foreground">
              {log.prompt_version}
            </span>
            {log.confidence != null && (
              <span className="shrink-0 text-[10px] text-muted-foreground">
                {(log.confidence * 100).toFixed(0)}% conf
              </span>
            )}
          </div>
          <p className="mt-0.5 truncate text-xs text-muted-foreground">
            {log.prompt.slice(0, 120)}
            {log.prompt.length > 120 ? "..." : ""}
          </p>
        </div>

        <div className="flex shrink-0 items-center gap-3 text-xs text-muted-foreground">
          {log.execution_time_ms != null && (
            <span className="hidden sm:inline">{log.execution_time_ms}ms</span>
          )}
          {log.input_tokens != null && (
            <span className="hidden sm:inline">
              ↑{log.input_tokens} ↓{log.output_tokens ?? 0}
            </span>
          )}
          <span>{createdDate.toLocaleString()}</span>
        </div>
      </button>

      {isExpanded && (
        <div className="border-t px-4 py-4">
          <LogDetail log={log} />
        </div>
      )}
    </div>
  )
}

function useFilterLogs(
  logsData: PaginatedResponse<AILog> | undefined,
  searchText: string,
): AILog[] {
  if (!logsData) return []

  if (!searchText) return logsData.items

  const lower = searchText.toLowerCase()
  return logsData.items.filter((log) => {
    if (log.model.toLowerCase().includes(lower)) return true
    if (log.prompt_version.toLowerCase().includes(lower)) return true
    if (log.prompt.toLowerCase().includes(lower)) return true
    if (log.response.toLowerCase().includes(lower)) return true
    if (log.error_message?.toLowerCase().includes(lower)) return true
    if (log.ticket_id?.toLowerCase().includes(lower)) return true
    if (
      log.parsed_json &&
      JSON.stringify(log.parsed_json).toLowerCase().includes(lower)
    )
      return true
    return false
  })
}
