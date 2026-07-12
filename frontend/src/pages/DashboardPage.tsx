import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  AlertCircle,
  CalendarClock,
  CheckCircle,
  ListChecks,
} from "lucide-react"

export function DashboardPage() {
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Tasks</CardTitle>
            <ListChecks className="size-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">0</div>
            <p className="text-xs text-muted-foreground">No tasks yet</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Pending Info</CardTitle>
            <AlertCircle className="size-4 text-amber-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">0</div>
            <p className="text-xs text-muted-foreground">Awaiting responses</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Ready to Schedule</CardTitle>
            <CalendarClock className="size-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">0</div>
            <p className="text-xs text-muted-foreground">Needs scheduling</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Tasks</CardTitle>
            <CheckCircle className="size-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">0</div>
            <p className="text-xs text-muted-foreground">In progress</p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardContent className="flex flex-col items-center justify-center py-12 text-center">
          <div className="rounded-full bg-muted p-4">
            <ListChecks className="size-8 text-muted-foreground" />
          </div>
          <h3 className="mt-4 text-lg font-medium">Welcome to AI Task Manager</h3>
          <p className="mt-1 max-w-md text-sm text-muted-foreground">
            This dashboard provides an overview of your task management system.
            Use the sidebar to navigate between queues, or press{" "}
            <kbd className="rounded border bg-muted px-1.5 py-0.5 font-mono text-xs">
              1-5
            </kbd>{" "}
            to switch views.
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
