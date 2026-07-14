import { useState } from "react"
import { useNavigate } from "react-router-dom"
import type { SchedulingQueueItem, ScheduleBlock } from "@/services/api"
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import { CalendarPreview } from "@/components/CalendarPreview"
import { ScheduleApprovalModal } from "@/components/ScheduleApprovalModal"
import {
  CheckCircle,
  XCircle,
  Pencil,
  CalendarClock,
  FolderOpen,
  Clock,
  ChevronDown,
  ChevronUp,
} from "lucide-react"

interface ScheduleCardProps {
  item: SchedulingQueueItem
  onApprove: (ticketId: string, blocks?: ScheduleBlock[]) => void
  onDecline: (ticketId: string, reason?: string) => void
  onModify: (ticketId: string, blocks: ScheduleBlock[]) => void
  isPending: boolean
}

function confidenceColor(level: string): string {
  switch (level) {
    case "HIGH":
      return "text-green-600 bg-green-50 border-green-200 dark:text-green-400 dark:bg-green-950 dark:border-green-800"
    case "MEDIUM":
      return "text-amber-600 bg-amber-50 border-amber-200 dark:text-amber-400 dark:bg-amber-950 dark:border-amber-800"
    case "LOW":
      return "text-red-600 bg-red-50 border-red-200 dark:text-red-400 dark:bg-red-950 dark:border-red-800"
    default:
      return "text-muted-foreground bg-muted border-border"
  }
}

export function ScheduleCard({
  item,
  onApprove,
  onDecline,
  onModify,
  isPending,
}: ScheduleCardProps) {
  const [showBlocks, setShowBlocks] = useState(true)
  const [approvalMode, setApprovalMode] = useState<
    "approve" | "decline" | "modify" | null
  >(null)
  const navigate = useNavigate()

  const confidence = item.confidence_indicator
  const ticketIdShort = item.ticket_id.slice(0, 8)
  const { suggestion } = item

  function handleConfirmApprove() {
    onApprove(item.ticket_id)
    setApprovalMode(null)
  }

  function handleConfirmDecline(reason?: string) {
    onDecline(item.ticket_id, reason)
    setApprovalMode(null)
  }

  function handleConfirmModify(blocks: ScheduleBlock[]) {
    onModify(item.ticket_id, blocks)
    setApprovalMode(null)
  }

  return (
    <>
      <Card>
        <CardHeader>
          <div className="flex items-start justify-between">
            <div className="space-y-1">
              <CardTitle className="flex items-center gap-2">
                <CalendarClock className="size-4 shrink-0 text-muted-foreground" />
                <button
                  type="button"
                  onClick={() => navigate(`/active-tasks/${item.ticket_id}`)}
                  className="hover:underline"
                >
                  Ticket {ticketIdShort}...
                </button>
              </CardTitle>
              <div className="flex items-center gap-3 text-xs text-muted-foreground">
                <span className="flex items-center gap-1">
                  <FolderOpen className="size-3" />
                  {item.ticket_id}
                </span>
                <span>·</span>
                <span className="flex items-center gap-1">
                  <Clock className="size-3" />
                  {new Date(item.created_at).toLocaleDateString()}
                </span>
              </div>
            </div>
            <div
              className={cn(
                "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium",
                confidenceColor(confidence.level),
              )}
            >
              {confidence.label}
              <span className="ml-1 text-[10px] opacity-70">
                ({Math.round(item.confidence * 100)}%)
              </span>
            </div>
          </div>
        </CardHeader>

        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
              Schedule Blocks
            </p>
            <button
              type="button"
              onClick={() => setShowBlocks(!showBlocks)}
              className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground"
            >
              {showBlocks ? (
                <>
                  <ChevronUp className="size-3" /> Hide
                </>
              ) : (
                <>
                  <ChevronDown className="size-3" /> Show
                </>
              )}
            </button>
          </div>

          {showBlocks && (
            <CalendarPreview
              blocks={suggestion.blocks}
              totalHours={suggestion.total_hours}
              fitsDeadline={suggestion.fits_deadline}
            />
          )}
        </CardContent>

        <CardFooter className="gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setApprovalMode("modify")}
            disabled={isPending}
          >
            <Pencil className="size-3.5" />
            Modify
          </Button>
          <Button
            size="sm"
            onClick={() => setApprovalMode("approve")}
            disabled={isPending}
          >
            <CheckCircle className="size-3.5" />
            Accept
          </Button>
          <Button
            variant="destructive"
            size="sm"
            onClick={() => setApprovalMode("decline")}
            disabled={isPending}
          >
            <XCircle className="size-3.5" />
            Decline
          </Button>
        </CardFooter>
      </Card>

      {approvalMode && (
        <ScheduleApprovalModal
          ticketId={item.ticket_id}
          mode={approvalMode}
          blocks={suggestion.blocks}
          onConfirmApprove={handleConfirmApprove}
          onConfirmDecline={handleConfirmDecline}
          onConfirmModify={handleConfirmModify}
          onCancel={() => setApprovalMode(null)}
        />
      )}
    </>
  )
}
