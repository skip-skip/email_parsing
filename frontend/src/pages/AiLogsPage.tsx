import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"

export function AiLogsPage() {
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold tracking-tight">AI Logs</h1>
      <Card>
        <CardHeader>
          <CardTitle>No logs yet</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">
            AI interaction logs will appear here for review and debugging.
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
