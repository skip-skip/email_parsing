import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export function SchedulingPage() {
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold tracking-tight">Scheduling Queue</h1>
      <Card>
        <CardHeader>
          <CardTitle>No items to schedule</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">
            Tasks ready for scheduling will appear here.
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
