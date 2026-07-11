import { NavLink, Outlet } from "react-router-dom"
import { cn } from "@/lib/utils"

const navItems = [
  { to: "/", label: "Dashboard" },
  { to: "/missing-info", label: "Missing Info Queue" },
  { to: "/scheduling", label: "Scheduling Queue" },
  { to: "/active-tasks", label: "Active Tasks" },
]

export function Layout() {
  return (
    <div className="flex h-screen bg-background">
      <aside className="w-64 border-r bg-sidebar text-sidebar-foreground">
        <div className="flex h-14 items-center border-b px-4">
          <h2 className="text-lg font-semibold">AI Task Manager</h2>
        </div>
        <nav className="space-y-1 p-2">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === "/"}
              className={({ isActive }) =>
                cn(
                  "block rounded-md px-3 py-2 text-sm font-medium transition-colors",
                  isActive
                    ? "bg-sidebar-accent text-sidebar-accent-foreground"
                    : "text-sidebar-foreground hover:bg-sidebar-accent/50",
                )
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
      </aside>
      <main className="flex-1 overflow-y-auto p-6">
        <Outlet />
      </main>
    </div>
  )
}
