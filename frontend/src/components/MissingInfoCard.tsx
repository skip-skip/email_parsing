import { useState } from "react"
import { useNavigate } from "react-router-dom"
import type { QueueItem } from "@/services/api"
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import { DraftEditor } from "@/components/DraftEditor"
import { ApprovalModal } from "@/components/ApprovalModal"
import {
  Pencil,
  CheckCircle,
  XCircle,
  ChevronDown,
  ChevronUp,
  Mail,
  User,
  FileText,
  Clock,
  Send,
} from "lucide-react"

interface MissingInfoCardProps {
  item: QueueItem
  onApprove: (ticketId: string, edits?: QueueItem["draft_email"]) => void
  onReject: (ticketId: string, reason?: string) => void
  onUpdateDraft: (
    ticketId: string,
    draft: QueueItem["draft_email"],
  ) => void
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

export function MissingInfoCard({
  item,
  onApprove,
  onReject,
  onUpdateDraft,
  isPending,
}: MissingInfoCardProps) {
  const [isEditing, setIsEditing] = useState(false)
  const [showDraft, setShowDraft] = useState(false)
  const [approvalMode, setApprovalMode] = useState<"approve" | "reject" | null>(
    null,
  )
  const navigate = useNavigate()

  const confidence = item.confidence_indicator
  const ticketIdShort = item.ticket_id.slice(0, 8)
  const isAwaitingReply = item.status === "AWAITING_REPLY"

  function handleSaveDraft(draft: QueueItem["draft_email"]) {
    onUpdateDraft(item.ticket_id, draft)
    setIsEditing(false)
  }

  function handleConfirmApproval(reason?: string) {
    if (approvalMode === "approve") {
      onApprove(item.ticket_id)
    } else {
      onReject(item.ticket_id, reason)
    }
    setApprovalMode(null)
  }

  return (
    <>
      <Card>
        <CardHeader>
          <div className="flex items-start justify-between">
            <div className="space-y-1">
              <CardTitle className="flex items-center gap-2">
                {isAwaitingReply ? (
                  <Clock className="size-4 shrink-0 text-blue-500" />
                ) : (
                  <FileText className="size-4 shrink-0 text-muted-foreground" />
                )}
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
                  <User className="size-3" />
                  {item.draft_email.to || "No recipient"}
                </span>
                <span>·</span>
                <span>{new Date(item.created_at).toLocaleDateString()}</span>
              </div>
            </div>
            <div className="flex items-center gap-2">
              {isAwaitingReply && (
                <span className="inline-flex items-center gap-1 rounded-full border border-blue-200 bg-blue-50 px-2.5 py-0.5 text-xs font-medium text-blue-700 dark:border-blue-800 dark:bg-blue-950 dark:text-blue-300">
                  <Send className="size-3" />
                  Email Sent
                </span>
              )}
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
          </div>
        </CardHeader>

        <CardContent className="space-y-4">
          {/* Missing fields */}
          {item.missing_fields.length > 0 && (
            <div className="space-y-1.5">
              <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                Missing Fields
              </p>
              <div className="flex flex-wrap gap-1.5">
                {item.missing_fields.map((field) => (
                  <span
                    key={field}
                    className={cn(
                      "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium",
                      "border-amber-300 bg-amber-50 text-amber-800",
                      "dark:border-amber-700 dark:bg-amber-950 dark:text-amber-200",
                    )}
                  >
                    {field}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Draft preview / editor */}
          {isEditing ? (
            <DraftEditor
              draft={item.draft_email}
              missingFields={item.missing_fields}
              onSave={handleSaveDraft}
              onCancel={() => setIsEditing(false)}
            />
          ) : (
            <div className="space-y-1.5">
              <div className="flex items-center justify-between">
                <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                  {isAwaitingReply ? "Sent Email" : "Draft Response"}
                </p>
                <button
                  type="button"
                  onClick={() => setShowDraft(!showDraft)}
                  className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground"
                >
                  {showDraft ? (
                    <>
                      <ChevronUp className="size-3" /> Hide
                    </>
                  ) : (
                    <>
                      <ChevronDown className="size-3" /> Preview
                    </>
                  )}
                </button>
              </div>
              {showDraft && (
                <div className="rounded-md border bg-muted/50 p-3 text-sm">
                  <div className="flex items-center gap-1 text-xs text-muted-foreground">
                    <Mail className="size-3" />
                    <span>To: {item.draft_email.to}</span>
                  </div>
                  <p className="mt-1 font-medium">{item.draft_email.subject}</p>
                  <p className="mt-1 whitespace-pre-wrap text-muted-foreground">
                    {item.draft_email.body}
                  </p>
                </div>
              )}
            </div>
          )}

          {/* Awaiting reply status message */}
          {isAwaitingReply && (
            <div className="rounded-md border border-blue-200 bg-blue-50 p-3 text-sm text-blue-700 dark:border-blue-800 dark:bg-blue-950 dark:text-blue-300">
              <p className="font-medium">Email sent — awaiting reply</p>
              <p className="mt-1 text-xs opacity-80">
                The missing information request has been sent. When the sender
                replies, the system will automatically process their response.
              </p>
            </div>
          )}
        </CardContent>

        {!isEditing && !isAwaitingReply && (
          <CardFooter className="gap-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsEditing(true)}
              disabled={isPending}
            >
              <Pencil className="size-3.5" />
              Edit Draft
            </Button>
            <Button
              size="sm"
              onClick={() => setApprovalMode("approve")}
              disabled={isPending}
            >
              <CheckCircle className="size-3.5" />
              Approve & Send
            </Button>
            <Button
              variant="destructive"
              size="sm"
              onClick={() => setApprovalMode("reject")}
              disabled={isPending}
            >
              <XCircle className="size-3.5" />
              Reject
            </Button>
          </CardFooter>
        )}
      </Card>

      {approvalMode && (
        <ApprovalModal
          ticketId={item.ticket_id}
          mode={approvalMode}
          onConfirm={handleConfirmApproval}
          onCancel={() => setApprovalMode(null)}
        />
      )}
    </>
  )
}
