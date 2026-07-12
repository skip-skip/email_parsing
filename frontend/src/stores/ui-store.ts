import { create } from "zustand"
import { persist } from "zustand/middleware"

export type SortDirection = "asc" | "desc"

interface UIState {
  sidebarCollapsed: boolean
  toggleSidebar: () => void

  activeSortField: string | null
  activeSortDirection: SortDirection
  setSortField: (field: string, direction?: SortDirection) => void
  clearSort: () => void

  searchQuery: string
  setSearchQuery: (query: string) => void
  clearSearch: () => void

  selectedTicketIds: Set<string>
  toggleTicketSelection: (ticketId: string) => void
  selectAllTickets: (ticketIds: string[]) => void
  clearSelection: () => void
}

export const useUIStore = create<UIState>()(
  persist(
    (set) => ({
      sidebarCollapsed: false,
      toggleSidebar: () =>
        set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),

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
    }),
    {
      name: "ai-task-manager-ui",
      partialize: (state) => ({
        sidebarCollapsed: state.sidebarCollapsed,
      }),
    },
  ),
)
