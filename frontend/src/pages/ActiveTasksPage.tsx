import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export function ActiveTasksPage() {
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold tracking-tight">Active Tasks</h1>
      <Card>
        <CardHeader>
          <CardTitle>No active tasks</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">
            Accepted tasks with calendar events will appear here.
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
