import type { ScheduleBlock } from "@/services/api"
import { Calendar, Clock } from "lucide-react"

interface CalendarPreviewProps {
  blocks: ScheduleBlock[]
  totalHours: number
  fitsDeadline: boolean
}

function formatDateTime(iso: string): { day: string; time: string } {
  const date = new Date(iso)
  const day = date.toLocaleDateString("en-US", {
    weekday: "long",
    month: "short",
    day: "numeric",
  })
  const time = date.toLocaleTimeString("en-US", {
    hour: "numeric",
    minute: "2-digit",
    hour12: true,
  })
  return { day, time }
}

function groupBlocksByDay(blocks: ScheduleBlock[]): Map<string, ScheduleBlock[]> {
  const grouped = new Map<string, ScheduleBlock[]>()
  for (const block of blocks) {
    const date = new Date(block.start_time)
    const key = date.toISOString().split("T")[0]
    const existing = grouped.get(key) ?? []
    existing.push(block)
    grouped.set(key, existing)
  }
  return grouped
}

export function CalendarPreview({
  blocks,
  totalHours,
  fitsDeadline,
}: CalendarPreviewProps) {
  const grouped = groupBlocksByDay(blocks)

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
          Proposed Schedule
        </p>
        <div className="flex items-center gap-3 text-xs text-muted-foreground">
          <span className="flex items-center gap-1">
            <Clock className="size-3" />
            {totalHours}h total
          </span>
          <span
            className={
              fitsDeadline
                ? "text-green-600 dark:text-green-400"
                : "text-red-600 dark:text-red-400"
            }
          >
            {fitsDeadline ? "Fits deadline" : "Exceeds deadline"}
          </span>
        </div>
      </div>

      {blocks.length === 0 && (
        <p className="text-sm text-muted-foreground">No blocks scheduled.</p>
      )}

      {Array.from(grouped.entries()).map(([dateKey, dayBlocks]) => {
        const { day } = formatDateTime(dayBlocks[0].start_time)
        return (
          <div key={dateKey} className="rounded-lg border bg-muted/30 p-3">
            <div className="flex items-center gap-2 mb-2">
              <Calendar className="size-3.5 text-muted-foreground" />
              <span className="text-sm font-medium">{day}</span>
            </div>
            <div className="space-y-1.5 pl-5">
              {dayBlocks.map((block, idx) => {
                const start = formatDateTime(block.start_time)
                const end = formatDateTime(block.end_time)
                return (
                  <div
                    key={idx}
                    className="flex items-center gap-3 text-sm"
                  >
                    <span className="text-muted-foreground font-mono text-xs">
                      {start.time} – {end.time}
                    </span>
                    <span className="h-1.5 w-1.5 rounded-full bg-primary shrink-0" />
                    <span className="truncate">
                      {block.description || `${block.hours}h block`}
                    </span>
                    <span className="text-xs text-muted-foreground ml-auto shrink-0">
                      {block.hours}h
                    </span>
                  </div>
                )
              })}
            </div>
          </div>
        )
      })}
    </div>
  )
}
