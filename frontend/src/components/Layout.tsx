import { NavLink, Outlet } from "react-router-dom"
import {
  LayoutDashboard,
  AlertCircle,
  CalendarClock,
  ListChecks,
  ScrollText,
  Menu,
  PanelLeftClose,
} from "lucide-react"
import { cn } from "@/lib/utils"
import { useUIStore } from "@/stores/ui-store"

const navItems = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard },
  { to: "/missing-info", label: "Missing Info Queue", icon: AlertCircle },
  { to: "/scheduling", label: "Scheduling Queue", icon: CalendarClock },
  { to: "/active-tasks", label: "Active Tasks", icon: ListChecks },
  { to: "/ai-logs", label: "AI Logs", icon: ScrollText },
]

export function Layout() {
  const sidebarCollapsed = useUIStore((s) => s.sidebarCollapsed)
  const toggleSidebar = useUIStore((s) => s.toggleSidebar)

  return (
    <div className="flex h-screen bg-background">
      <aside
        className={cn(
          "flex flex-col border-r bg-sidebar text-sidebar-foreground transition-all duration-200",
          sidebarCollapsed ? "w-16" : "w-64",
        )}
      >
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
              {!sidebarCollapsed && <span>{item.label}</span>}
            </NavLink>
          ))}
        </nav>
        <div className="border-t p-2">
          <button
            type="button"
            onClick={toggleSidebar}
            className="flex w-full items-center gap-3 rounded-md px-3 py-2 text-sm font-medium text-sidebar-foreground transition-colors hover:bg-sidebar-accent/50"
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
      </aside>
      <div className="flex flex-1 flex-col overflow-hidden">
        <header className="flex h-14 items-center border-b px-6">
          <h1 className="text-sm font-medium text-muted-foreground">
            AI Task Management System
          </h1>
        </header>
        <main className="flex-1 overflow-y-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
