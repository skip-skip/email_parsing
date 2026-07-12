import { useState } from "react"
import type { AILog } from "@/services/api"
import {
  Card,
  CardContent,
} from "@/components/ui/card"
import { cn } from "@/lib/utils"
import {
  CheckCircle,
  XCircle,
  Clock,
  Cpu,
  Tag,
  Hash,
  Zap,
  ChevronDown,
  ChevronRight,
} from "lucide-react"

function tryFormatJson(value: string): string {
  try {
    const parsed = JSON.parse(value)
    return JSON.stringify(parsed, null, 2)
  } catch {
    return value
  }
}

function JsonBlock({ title, data }: { title: string; data: unknown }) {
  const [collapsed, setCollapsed] = useState(false)
  const formatted = JSON.stringify(data, null, 2)

  return (
    <div className="space-y-1">
      <button
        type="button"
        onClick={() => setCollapsed(!collapsed)}
        className="flex items-center gap-1.5 text-xs font-medium text-muted-foreground hover:text-foreground"
      >
        {collapsed ? (
          <ChevronRight className="size-3" />
        ) : (
          <ChevronDown className="size-3" />
        )}
        {title}
      </button>
      {!collapsed && (
        <pre className="overflow-x-auto rounded-lg border bg-muted/50 p-3 text-xs leading-relaxed">
          <code className="font-mono">{formatted}</code>
        </pre>
      )}
    </div>
  )
}

function TextBlock({ title, content }: { title: string; content: string }) {
  const [expanded, setExpanded] = useState(false)
  const isLong = content.length > 500
  const display = isLong && !expanded ? content.slice(0, 500) + "..." : content

  return (
    <div className="space-y-1">
      <p className="text-xs font-medium text-muted-foreground">{title}</p>
      <pre className="overflow-x-auto whitespace-pre-wrap rounded-lg border bg-muted/50 p-3 text-xs leading-relaxed">
        <code className="font-mono">{tryFormatJson(display)}</code>
      </pre>
      {isLong && (
        <button
          type="button"
          onClick={() => setExpanded(!expanded)}
          className="text-xs text-primary hover:underline"
        >
          {expanded ? "Show less" : "Show full content"}
        </button>
      )}
    </div>
  )
}

function MetadataRow({
  icon: Icon,
  label,
  value,
  className,
}: {
  icon: typeof Clock
  label: string
  value: React.ReactNode
  className?: string
}) {
  return (
    <div className="flex items-center gap-2">
      <Icon className={cn("size-3.5 shrink-0 text-muted-foreground", className)} />
      <span className="text-xs text-muted-foreground">{label}:</span>
      <span className="text-xs font-medium">{value}</span>
    </div>
  )
}

export function LogDetail({ log }: { log: AILog }) {
  const createdDate = new Date(log.created_at)

  return (
    <Card className="border-dashed">
      <CardContent className="space-y-4 pt-4">
        <div className="grid gap-3 sm:grid-cols-2">
          <div className="space-y-1">
            <MetadataRow
              icon={Cpu}
              label="Model"
              value={log.model}
            />
            <MetadataRow
              icon={Tag}
              label="Prompt Version"
              value={log.prompt_version}
            />
            <MetadataRow
              icon={Clock}
              label="Execution Time"
              value={
                log.execution_time_ms != null
                  ? `${log.execution_time_ms}ms`
                  : "N/A"
              }
            />
            <MetadataRow
              icon={Zap}
              label="Confidence"
              value={
                log.confidence != null
                  ? `${(log.confidence * 100).toFixed(1)}%`
                  : "N/A"
              }
            />
          </div>
          <div className="space-y-1">
            <MetadataRow
              icon={log.success ? CheckCircle : XCircle}
              label="Status"
              value={
                <span
                  className={cn(
                    "inline-flex items-center gap-1 rounded-full px-1.5 py-0.5 text-[10px] font-semibold",
                    log.success
                      ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400"
                      : "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
                  )}
                >
                  {log.success ? "Success" : "Failed"}
                </span>
              }
            />
            <MetadataRow
              icon={Hash}
              label="Ticket ID"
              value={
                log.ticket_id ? (
                  <span className="font-mono">{log.ticket_id.slice(0, 8)}...</span>
                ) : (
                  <span className="text-muted-foreground italic">None</span>
                )
              }
            />
            <MetadataRow
              icon={Zap}
              label="Tokens"
              value={
                log.input_tokens != null || log.output_tokens != null
                  ? `↑${log.input_tokens ?? 0} ↓${log.output_tokens ?? 0}`
                  : "N/A"
              }
            />
            <MetadataRow
              icon={Clock}
              label="Created"
              value={createdDate.toLocaleString()}
            />
          </div>
        </div>

        {log.error_message && (
          <div className="rounded-lg border border-red-200 bg-red-50 p-3 dark:border-red-800 dark:bg-red-950/50">
            <p className="text-xs font-medium text-red-700 dark:text-red-400">
              Error
            </p>
            <p className="mt-1 font-mono text-xs text-red-600 dark:text-red-300">
              {log.error_message}
            </p>
          </div>
        )}

        <TextBlock title="Prompt" content={log.prompt} />

        <TextBlock title="Response" content={log.response} />

        {log.parsed_json && (
          <JsonBlock title="Parsed JSON" data={log.parsed_json} />
        )}
      </CardContent>
    </Card>
  )
}
