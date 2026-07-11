import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export function MissingInfoPage() {
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold tracking-tight">Missing Information Queue</h1>
      <Card>
        <CardHeader>
          <CardTitle>No items in queue</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">
            Tasks with missing information will appear here for review.
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
