import { useState } from "react"
import type { ScheduleBlock } from "@/services/api"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import { CheckCircle, XCircle, Pencil, Plus } from "lucide-react"

interface ScheduleApprovalModalProps {
  ticketId: string
  mode: "approve" | "decline" | "modify"
  blocks: ScheduleBlock[]
  onConfirmApprove: () => void
  onConfirmDecline: (reason?: string) => void
  onConfirmModify: (blocks: ScheduleBlock[]) => void
  onCancel: () => void
}

function formatDateTime(iso: string): string {
  const date = new Date(iso)
  return date.toLocaleString("en-US", {
    weekday: "short",
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
    hour12: true,
  })
}

export function ScheduleApprovalModal({
  ticketId,
  mode,
  blocks,
  onConfirmApprove,
  onConfirmDecline,
  onConfirmModify,
  onCancel,
}: ScheduleApprovalModalProps) {
  const [reason, setReason] = useState("")
  const [editedBlocks, setEditedBlocks] = useState<ScheduleBlock[]>(
    blocks.map((b) => ({ ...b })),
  )

  function handleApprove() {
    onConfirmApprove()
  }

  function handleDecline() {
    onConfirmDecline(reason || undefined)
  }

  function handleModify() {
    onConfirmModify(editedBlocks)
  }

  function updateBlock(
    index: number,
    field: keyof ScheduleBlock,
    value: string | number,
  ) {
    setEditedBlocks((prev) =>
      prev.map((b, i) => (i === index ? { ...b, [field]: value } : b)),
    )
  }

  function removeBlock(index: number) {
    setEditedBlocks((prev) => prev.filter((_, i) => i !== index))
  }

  function addBlock() {
    const lastBlock = editedBlocks[editedBlocks.length - 1]
    const startDate = lastBlock
      ? new Date(new Date(lastBlock.end_time).getTime() + 60 * 60 * 1000)
      : new Date()
    const endDate = new Date(startDate.getTime() + 60 * 60 * 1000)
    setEditedBlocks((prev) => [
      ...prev,
      {
        start_time: startDate.toISOString(),
        end_time: endDate.toISOString(),
        hours: 1,
        description: "",
      },
    ])
  }

  const ticketIdShort = ticketId.slice(0, 8)

  const titles: Record<string, string> = {
    approve: "Accept Schedule",
    decline: "Decline Schedule",
    modify: "Modify Schedule",
  }

  const descriptions: Record<string, string> = {
    approve: `This will create Outlook calendar events for ticket ${ticketIdShort}... and send an acceptance email.`,
    decline: `This will decline the schedule for ticket ${ticketIdShort}... and send a decline email.`,
    modify: `Edit the proposed blocks below, then submit your modified schedule.`,
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center"
      role="dialog"
      aria-modal="true"
      aria-labelledby="schedule-approval-modal-title"
    >
      <div
        className="fixed inset-0 bg-black/50 backdrop-blur-sm"
        onClick={onCancel}
        onKeyDown={(e) => {
          if (e.key === "Escape") onCancel()
        }}
      />
      <div
        className={cn(
          "relative z-10 w-full max-w-lg rounded-xl border bg-background p-6 shadow-lg",
        )}
      >
        <h2
          id="schedule-approval-modal-title"
          className="text-lg font-semibold text-foreground"
        >
          {titles[mode]}
        </h2>
        <p className="mt-2 text-sm text-muted-foreground">
          {descriptions[mode]}
        </p>

        {mode === "decline" && (
          <div className="mt-4 space-y-1">
            <label
              htmlFor="decline-reason"
              className="text-sm font-medium text-foreground"
            >
              Reason (optional)
            </label>
            <textarea
              id="decline-reason"
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              rows={3}
              placeholder="Why is this schedule being declined?"
              className="w-full resize-y rounded-md border border-input bg-background px-3 py-2 text-sm outline-none focus:border-ring focus:ring-2 focus:ring-ring/50"
            />
          </div>
        )}

        {mode === "modify" && (
          <div className="mt-4 space-y-3 max-h-80 overflow-y-auto">
            {editedBlocks.map((block, idx) => (
              <div key={idx} className="rounded-lg border p-3 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-medium text-muted-foreground">
                    Block {idx + 1}
                  </span>
                  <button
                    type="button"
                    onClick={() => removeBlock(idx)}
                    className="text-xs text-destructive hover:underline"
                  >
                    Remove
                  </button>
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <div className="space-y-1">
                    <label
                      htmlFor={`block-start-${idx}`}
                      className="text-xs text-muted-foreground"
                    >
                      Start
                    </label>
                    <input
                      id={`block-start-${idx}`}
                      type="datetime-local"
                      value={block.start_time.slice(0, 16)}
                      onChange={(e) =>
                        updateBlock(
                          idx,
                          "start_time",
                          new Date(e.target.value).toISOString(),
                        )
                      }
                      className="w-full rounded-md border border-input bg-background px-2 py-1 text-sm outline-none focus:border-ring focus:ring-2 focus:ring-ring/50"
                    />
                  </div>
                  <div className="space-y-1">
                    <label
                      htmlFor={`block-end-${idx}`}
                      className="text-xs text-muted-foreground"
                    >
                      End
                    </label>
                    <input
                      id={`block-end-${idx}`}
                      type="datetime-local"
                      value={block.end_time.slice(0, 16)}
                      onChange={(e) =>
                        updateBlock(
                          idx,
                          "end_time",
                          new Date(e.target.value).toISOString(),
                        )
                      }
                      className="w-full rounded-md border border-input bg-background px-2 py-1 text-sm outline-none focus:border-ring focus:ring-2 focus:ring-ring/50"
                    />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <div className="space-y-1">
                    <label
                      htmlFor={`block-hours-${idx}`}
                      className="text-xs text-muted-foreground"
                    >
                      Hours
                    </label>
                    <input
                      id={`block-hours-${idx}`}
                      type="number"
                      min={0.5}
                      step={0.5}
                      value={block.hours}
                      onChange={(e) =>
                        updateBlock(
                          idx,
                          "hours",
                          parseFloat(e.target.value) || 0,
                        )
                      }
                      className="w-full rounded-md border border-input bg-background px-2 py-1 text-sm outline-none focus:border-ring focus:ring-2 focus:ring-ring/50"
                    />
                  </div>
                  <div className="space-y-1">
                    <label
                      htmlFor={`block-desc-${idx}`}
                      className="text-xs text-muted-foreground"
                    >
                      Description
                    </label>
                    <input
                      id={`block-desc-${idx}`}
                      type="text"
                      value={block.description}
                      onChange={(e) =>
                        updateBlock(idx, "description", e.target.value)
                      }
                      placeholder="e.g. Design review"
                      className="w-full rounded-md border border-input bg-background px-2 py-1 text-sm outline-none focus:border-ring focus:ring-2 focus:ring-ring/50"
                    />
                  </div>
                </div>
              </div>
            ))}
            <Button variant="outline" size="sm" onClick={addBlock}>
              <Plus className="size-3.5" />
              Add Block
            </Button>
          </div>
        )}

        {mode === "approve" && (
          <div className="mt-4 space-y-2">
            {blocks.map((block, idx) => (
              <div
                key={idx}
                className="flex items-center gap-3 rounded-md border bg-muted/30 px-3 py-2 text-sm"
              >
                <span className="font-mono text-xs text-muted-foreground">
                  {formatDateTime(block.start_time)} –{" "}
                  {formatDateTime(block.end_time)}
                </span>
                <span className="text-xs text-muted-foreground">
                  {block.hours}h
                </span>
                {block.description && (
                  <span className="truncate text-xs">{block.description}</span>
                )}
              </div>
            ))}
          </div>
        )}

        <div className="mt-6 flex justify-end gap-2">
          <Button variant="outline" onClick={onCancel}>
            Cancel
          </Button>
          {mode === "approve" && (
            <Button onClick={handleApprove}>
              <CheckCircle className="size-3.5" />
              Accept Schedule
            </Button>
          )}
          {mode === "decline" && (
            <Button variant="destructive" onClick={handleDecline}>
              <XCircle className="size-3.5" />
              Decline
            </Button>
          )}
          {mode === "modify" && (
            <Button onClick={handleModify}>
              <Pencil className="size-3.5" />
              Submit Modified Schedule
            </Button>
          )}
        </div>
      </div>
    </div>
  )
}
