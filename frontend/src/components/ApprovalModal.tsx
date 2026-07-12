import { useState } from "react"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

interface ApprovalModalProps {
  ticketId: string
  mode: "approve" | "reject"
  onConfirm: (reason?: string) => void
  onCancel: () => void
}

export function ApprovalModal({
  ticketId,
  mode,
  onConfirm,
  onCancel,
}: ApprovalModalProps) {
  const [reason, setReason] = useState("")

  function handleConfirm() {
    onConfirm(mode === "reject" ? reason : undefined)
  }

  const isApprove = mode === "approve"

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center"
      role="dialog"
      aria-modal="true"
      aria-labelledby="approval-modal-title"
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
          "relative z-10 w-full max-w-md rounded-xl border bg-background p-6 shadow-lg",
        )}
      >
        <h2
          id="approval-modal-title"
          className="text-lg font-semibold text-foreground"
        >
          {isApprove ? "Approve & Send" : "Reject Draft"}
        </h2>
        <p className="mt-2 text-sm text-muted-foreground">
          {isApprove
            ? `This will send the drafted email for ticket ${ticketId.slice(0, 8)}... and move it out of the queue.`
            : `This will reject the draft for ticket ${ticketId.slice(0, 8)}... and remove it from the queue.`}
        </p>

        {mode === "reject" && (
          <div className="mt-4 space-y-1">
            <label
              htmlFor="reject-reason"
              className="text-sm font-medium text-foreground"
            >
              Reason (optional)
            </label>
            <textarea
              id="reject-reason"
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              rows={3}
              placeholder="Why is this draft being rejected?"
              className="w-full resize-y rounded-md border border-input bg-background px-3 py-2 text-sm outline-none focus:border-ring focus:ring-2 focus:ring-ring/50"
            />
          </div>
        )}

        <div className="mt-6 flex justify-end gap-2">
          <Button variant="outline" onClick={onCancel}>
            Cancel
          </Button>
          <Button
            variant={isApprove ? "default" : "destructive"}
            onClick={handleConfirm}
          >
            {isApprove ? "Approve & Send" : "Reject"}
          </Button>
        </div>
      </div>
    </div>
  )
}
