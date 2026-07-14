import { NavLink, Outlet, useLocation } from "react-router-dom"
import {
  LayoutDashboard,
  AlertCircle,
  CalendarClock,
  ListChecks,
  CheckCircle2,
  ScrollText,
  Menu,
  PanelLeftClose,
  X,
} from "lucide-react"
import { cn } from "@/lib/utils"
import { useUIStore } from "@/stores/ui-store"
import { ThemeToggle } from "@/components/ThemeToggle"
import { useKeyboardShortcuts } from "@/hooks/useKeyboardShortcuts"
import { useEffect } from "react"

const navItems = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard, key: "1" },
  { to: "/missing-info", label: "Missing Info Queue", icon: AlertCircle, key: "2" },
  { to: "/scheduling", label: "Scheduling Queue", icon: CalendarClock, key: "3" },
  { to: "/active-tasks", label: "Active Tasks", icon: ListChecks, key: "4" },
  { to: "/closed-tasks", label: "Closed Tasks", icon: CheckCircle2, key: "5" },
  { to: "/ai-logs", label: "AI Logs", icon: ScrollText, key: "6" },
]

export function Layout() {
  const sidebarCollapsed = useUIStore((s) => s.sidebarCollapsed)
  const toggleSidebar = useUIStore((s) => s.toggleSidebar)
  const mobileSidebarOpen = useUIStore((s) => s.mobileSidebarOpen)
  const setMobileSidebarOpen = useUIStore((s) => s.setMobileSidebarOpen)
  const lastUpdated = useUIStore((s) => s.lastUpdated)
  const location = useLocation()

  const { navigate } = useKeyboardShortcuts({
    "1": () => navigate("/"),
    "2": () => navigate("/missing-info"),
    "3": () => navigate("/scheduling"),
    "4": () => navigate("/active-tasks"),
    "5": () => navigate("/closed-tasks"),
    "6": () => navigate("/ai-logs"),
    d: () => useUIStore.getState().toggleTheme(),
  })

  useEffect(() => {
    setMobileSidebarOpen(false)
  }, [location.pathname, setMobileSidebarOpen])

  const currentTimestamp = (() => {
    const pageKey = location.pathname
    const ts = lastUpdated[pageKey]
    if (!ts) return null
    const date = new Date(ts)
    return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" })
  })()

  const sidebarContent = (
    <>
      <div className="flex h-14 items-center border-b px-4">
        {!sidebarCollapsed && (
          <h2 className="text-lg font-semibold">AI Task Manager</h2>
        )}
      </div>
      <nav className="flex-1 space-y-1 p-2">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === "/"}
            className={({ isActive }) =>
              cn(
                "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                isActive
                  ? "bg-sidebar-accent text-sidebar-accent-foreground"
                  : "text-sidebar-foreground hover:bg-sidebar-accent/50",
              )
            }
          >
            <item.icon className="size-4 shrink-0" />
            {!sidebarCollapsed && (
              <span className="flex-1">{item.label}</span>
            )}
            {!sidebarCollapsed && (
              <kbd className="pointer-events-none hidden rounded border bg-muted px-1.5 py-0.5 font-mono text-[10px] font-medium text-muted-foreground opacity-60 lg:inline-block">
                {item.key}
              </kbd>
            )}
          </NavLink>
        ))}
      </nav>
      <div className="border-t p-2">
        <button
          type="button"
          onClick={toggleSidebar}
          className="hidden w-full items-center gap-3 rounded-md px-3 py-2 text-sm font-medium text-sidebar-foreground transition-colors hover:bg-sidebar-accent/50 md:flex"
        >
          {sidebarCollapsed ? (
            <Menu className="size-4 shrink-0" />
          ) : (
            <>
              <PanelLeftClose className="size-4 shrink-0" />
              <span>Collapse</span>
            </>
          )}
        </button>
      </div>
    </>
  )

  return (
    <div className="flex h-screen bg-background">
      {/* Desktop sidebar */}
      <aside
        className={cn(
          "hidden flex-col border-r bg-sidebar text-sidebar-foreground transition-all duration-200 md:flex",
          sidebarCollapsed ? "w-16" : "w-64",
        )}
      >
        {sidebarContent}
      </aside>

      {/* Mobile sidebar overlay */}
      {mobileSidebarOpen && (
        <>
          <div
            className="fixed inset-0 z-40 bg-black/50 backdrop-blur-sm md:hidden"
            onClick={() => setMobileSidebarOpen(false)}
          />
          <aside className="fixed inset-y-0 left-0 z-50 flex w-64 flex-col border-r bg-sidebar text-sidebar-foreground md:hidden">
            <div className="flex h-14 items-center justify-between border-b px-4">
              <h2 className="text-lg font-semibold">AI Task Manager</h2>
              <button
                type="button"
                onClick={() => setMobileSidebarOpen(false)}
                className="rounded-md p-1 text-sidebar-foreground hover:bg-sidebar-accent/50"
              >
                <X className="size-4" />
              </button>
            </div>
            <nav className="flex-1 space-y-1 p-2">
              {navItems.map((item) => (
                <NavLink
                  key={item.to}
                  to={item.to}
                  end={item.to === "/"}
                  onClick={() => setMobileSidebarOpen(false)}
                  className={({ isActive }) =>
                    cn(
                      "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                      isActive
                        ? "bg-sidebar-accent text-sidebar-accent-foreground"
                        : "text-sidebar-foreground hover:bg-sidebar-accent/50",
                    )
                  }
                >
                  <item.icon className="size-4 shrink-0" />
                  <span>{item.label}</span>
                </NavLink>
              ))}
            </nav>
          </aside>
        </>
      )}

      <div className="flex flex-1 flex-col overflow-hidden">
        <header className="flex h-14 items-center justify-between border-b px-4 sm:px-6">
          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={() => setMobileSidebarOpen(true)}
              className="rounded-md p-1.5 text-muted-foreground hover:text-foreground md:hidden"
            >
              <Menu className="size-5" />
            </button>
            <h1 className="text-sm font-medium text-muted-foreground">
              AI Task Management System
            </h1>
            {currentTimestamp && (
              <span className="hidden text-xs text-muted-foreground sm:inline">
                Last updated: {currentTimestamp}
              </span>
            )}
          </div>
          <div className="flex items-center gap-1">
            <ThemeToggle />
          </div>
        </header>
        <main className="flex-1 overflow-y-auto p-4 sm:p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
