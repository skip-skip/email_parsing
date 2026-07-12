import { useState } from "react"
import type { DraftEmail } from "@/services/api"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

interface DraftEditorProps {
  draft: DraftEmail
  missingFields: string[]
  onSave: (draft: DraftEmail) => void
  onCancel: () => void
}

export function DraftEditor({
  draft,
  missingFields,
  onSave,
  onCancel,
}: DraftEditorProps) {
  const [to, setTo] = useState(draft.to)
  const [subject, setSubject] = useState(draft.subject)
  const [body, setBody] = useState(draft.body)

  function handleSave() {
    onSave({
      ...draft,
      to,
      subject,
      body,
      missing_fields: missingFields,
    })
  }

  return (
    <div className="space-y-4">
      <div className="space-y-1">
        <label
          htmlFor="draft-to"
          className="text-sm font-medium text-foreground"
        >
          To
        </label>
        <input
          id="draft-to"
          type="email"
          value={to}
          onChange={(e) => setTo(e.target.value)}
          className="w-full rounded-md border border-input bg-background px-3 py-1.5 text-sm outline-none focus:border-ring focus:ring-2 focus:ring-ring/50"
        />
      </div>
      <div className="space-y-1">
        <label
          htmlFor="draft-subject"
          className="text-sm font-medium text-foreground"
        >
          Subject
        </label>
        <input
          id="draft-subject"
          type="text"
          value={subject}
          onChange={(e) => setSubject(e.target.value)}
          className="w-full rounded-md border border-input bg-background px-3 py-1.5 text-sm outline-none focus:border-ring focus:ring-2 focus:ring-ring/50"
        />
      </div>
      <div className="space-y-1">
        <label
          htmlFor="draft-body"
          className="text-sm font-medium text-foreground"
        >
          Body
        </label>
        <textarea
          id="draft-body"
          value={body}
          onChange={(e) => setBody(e.target.value)}
          rows={10}
          className="w-full resize-y rounded-md border border-input bg-background px-3 py-2 text-sm outline-none focus:border-ring focus:ring-2 focus:ring-ring/50"
        />
      </div>
      {missingFields.length > 0 && (
        <div className="space-y-1">
          <p className="text-sm font-medium text-foreground">
            Missing fields to request:
          </p>
          <div className="flex flex-wrap gap-1.5">
            {missingFields.map((field) => (
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
      <div className="flex justify-end gap-2">
        <Button variant="outline" onClick={onCancel}>
          Cancel
        </Button>
        <Button onClick={handleSave}>Save Changes</Button>
      </div>
    </div>
  )
}
