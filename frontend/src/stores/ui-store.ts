import { create } from "zustand"
import { persist } from "zustand/middleware"

export type SortDirection = "asc" | "desc"
export type Theme = "light" | "dark"

interface UIState {
  sidebarCollapsed: boolean
  toggleSidebar: () => void
  mobileSidebarOpen: boolean
  setMobileSidebarOpen: (open: boolean) => void

  theme: Theme
  toggleTheme: () => void

  activeSortField: string | null
  activeSortDirection: SortDirection
  setSortField: (field: string, direction?: SortDirection) => void
  clearSort: () => void

  searchQuery: string
  setSearchQuery: (query: string) => void
  clearSearch: () => void

  activeTaskStatusFilter: string
  setActiveTaskStatusFilter: (status: string) => void
  activeTaskClientFilter: string
  setActiveTaskClientFilter: (client: string) => void

  selectedTicketIds: Set<string>
  toggleTicketSelection: (ticketId: string) => void
  selectAllTickets: (ticketIds: string[]) => void
  clearSelection: () => void

  lastUpdated: Record<string, number>
  setLastUpdated: (key: string) => void
}

function applyTheme(theme: Theme) {
  const root = document.documentElement
  if (theme === "dark") {
    root.classList.add("dark")
  } else {
    root.classList.remove("dark")
  }
}

export const useUIStore = create<UIState>()(
  persist(
    (set) => ({
      sidebarCollapsed: false,
      toggleSidebar: () =>
        set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),
      mobileSidebarOpen: false,
      setMobileSidebarOpen: (open) => set({ mobileSidebarOpen: open }),

      theme: "light" as Theme,
      toggleTheme: () =>
        set((state) => {
          const next: Theme = state.theme === "light" ? "dark" : "light"
          applyTheme(next)
          return { theme: next }
        }),

      activeSortField: null,
      activeSortDirection: "asc",
      setSortField: (field, direction = "asc") =>
        set((state) => ({
          activeSortField: field,
          activeSortDirection:
            state.activeSortField === field && state.activeSortDirection === "asc"
              ? "desc"
              : direction,
        })),
      clearSort: () => set({ activeSortField: null, activeSortDirection: "asc" }),

      searchQuery: "",
      setSearchQuery: (query) => set({ searchQuery: query }),
      clearSearch: () => set({ searchQuery: "" }),

      activeTaskStatusFilter: "",
      setActiveTaskStatusFilter: (status) => set({ activeTaskStatusFilter: status }),
      activeTaskClientFilter: "",
      setActiveTaskClientFilter: (client) => set({ activeTaskClientFilter: client }),

      selectedTicketIds: new Set<string>(),
      toggleTicketSelection: (ticketId) =>
        set((state) => {
          const next = new Set(state.selectedTicketIds)
          if (next.has(ticketId)) {
            next.delete(ticketId)
          } else {
            next.add(ticketId)
          }
          return { selectedTicketIds: next }
        }),
      selectAllTickets: (ticketIds) =>
        set({ selectedTicketIds: new Set(ticketIds) }),
      clearSelection: () => set({ selectedTicketIds: new Set<string>() }),

      lastUpdated: {} as Record<string, number>,
      setLastUpdated: (key) =>
        set((state) => ({
          lastUpdated: { ...state.lastUpdated, [key]: Date.now() },
        })),
    }),
    {
      name: "ai-task-manager-ui",
      partialize: (state) => ({
        sidebarCollapsed: state.sidebarCollapsed,
        theme: state.theme,
      }),
      onRehydrateStorage: () => (state) => {
        if (state?.theme) {
          applyTheme(state.theme)
        }
      },
    },
  ),
)
