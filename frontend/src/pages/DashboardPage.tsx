import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  AlertCircle,
  CalendarClock,
  CheckCircle,
  ListChecks,
  Loader2,
  Wifi,
  WifiOff,
} from "lucide-react"
import { api, type LLMHealth } from "@/services/api"

interface DashboardStats {
  activeTasks: number
  pendingInfo: number
  readyToSchedule: number
}

export function DashboardPage() {
  const navigate = useNavigate()
  const [stats, setStats] = useState<DashboardStats>({
    activeTasks: 0,
    pendingInfo: 0,
    readyToSchedule: 0,
  })
  const [llmHealth, setLlmHealth] = useState<LLMHealth | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false

    async function fetchDashboardData() {
      try {
        setLoading(true)
        setError(null)

        const [activeRes, missingRes, schedulingRes, healthRes] =
          await Promise.allSettled([
            api.tickets.listActive(),
            api.missingInfo.list(),
            api.scheduling.list(),
            api.llm.health(),
          ])

        if (cancelled) return

        setStats({
          activeTasks:
            activeRes.status === "fulfilled" ? activeRes.value.data.total : 0,
          pendingInfo:
            missingRes.status === "fulfilled"
              ? missingRes.value.data.length
              : 0,
          readyToSchedule:
            schedulingRes.status === "fulfilled"
              ? schedulingRes.value.data.length
              : 0,
        })

        if (healthRes.status === "fulfilled") {
          setLlmHealth(healthRes.value.data)
        }
      } catch {
        if (!cancelled) {
          setError("Failed to load dashboard data")
        }
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    fetchDashboardData()

    return () => {
      cancelled = true
    }
  }, [])

  const totalTasks =
    stats.activeTasks + stats.pendingInfo + stats.readyToSchedule

  const cards = [
    {
      title: "Total Tasks",
      value: totalTasks,
      subtitle: totalTasks === 0 ? "No tasks yet" : "Across all queues",
      icon: ListChecks,
      iconColor: "text-muted-foreground",
      onClick: () => navigate("/active-tasks"),
    },
    {
      title: "Pending Info",
      value: stats.pendingInfo,
      subtitle:
        stats.pendingInfo === 0 ? "No pending items" : "Awaiting responses",
      icon: AlertCircle,
      iconColor: "text-amber-500",
      onClick: () => navigate("/missing-info"),
    },
    {
      title: "Ready to Schedule",
      value: stats.readyToSchedule,
      subtitle:
        stats.readyToSchedule === 0
          ? "Nothing to schedule"
          : "Needs scheduling",
      icon: CalendarClock,
      iconColor: "text-blue-500",
      onClick: () => navigate("/scheduling"),
    },
    {
      title: "Active Tasks",
      value: stats.activeTasks,
      subtitle: stats.activeTasks === 0 ? "No active tasks" : "In progress",
      icon: CheckCircle,
      iconColor: "text-green-500",
      onClick: () => navigate("/active-tasks"),
    },
  ]

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>

      {error && (
        <div className="rounded-md bg-red-50 p-4 text-sm text-red-800 dark:bg-red-950 dark:text-red-200">
          {error}
        </div>
      )}

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {cards.map((card) => (
          <button
            key={card.title}
            type="button"
            onClick={card.onClick}
            className="text-left transition-transform hover:scale-[1.02]"
          >
            <Card className="h-full cursor-pointer">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  {card.title}
                </CardTitle>
                <card.icon className={`size-4 ${card.iconColor}`} />
              </CardHeader>
              <CardContent>
                {loading ? (
                  <Loader2 className="size-6 animate-spin text-muted-foreground" />
                ) : (
                  <div className="text-2xl font-bold">{card.value}</div>
                )}
                <p className="text-xs text-muted-foreground">
                  {card.subtitle}
                </p>
              </CardContent>
            </Card>
          </button>
        ))}
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">LLM Status</CardTitle>
            {llmHealth?.status === "healthy" ? (
              <Wifi className="size-4 text-green-500" />
            ) : (
              <WifiOff className="size-4 text-red-500" />
            )}
          </CardHeader>
          <CardContent>
            {loading ? (
              <Loader2 className="size-4 animate-spin text-muted-foreground" />
            ) : llmHealth ? (
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span
                    className={`inline-block size-2 rounded-full ${
                      llmHealth.status === "healthy"
                        ? "bg-green-500"
                        : "bg-red-500"
                    }`}
                  />
                  <span className="text-sm font-medium capitalize">
                    {llmHealth.status}
                  </span>
                </div>
                {llmHealth.fallback_chain.length > 0 && (
                  <p className="text-xs text-muted-foreground">
                    Model: {llmHealth.fallback_chain[0]}
                  </p>
                )}
                {llmHealth.usage_stats.total_requests > 0 && (
                  <p className="text-xs text-muted-foreground">
                    {llmHealth.usage_stats.total_requests} requests (
                    {llmHealth.usage_stats.successful_requests} successful)
                  </p>
                )}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">Unknown</p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Quick Actions</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <button
              type="button"
              onClick={() => navigate("/active-tasks")}
              className="w-full rounded-md bg-primary px-3 py-2 text-left text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90"
            >
              View Active Tasks
            </button>
            <button
              type="button"
              onClick={() => navigate("/missing-info")}
              className="w-full rounded-md border px-3 py-2 text-left text-sm font-medium transition-colors hover:bg-muted"
            >
              Check Missing Info Queue
            </button>
            <button
              type="button"
              onClick={() => navigate("/scheduling")}
              className="w-full rounded-md border px-3 py-2 text-left text-sm font-medium transition-colors hover:bg-muted"
            >
              Review Scheduling Queue
            </button>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
