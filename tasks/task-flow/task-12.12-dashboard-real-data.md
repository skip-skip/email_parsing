# Task 12.12 — Dashboard: Wire Up Real Data

## Description
The Dashboard page is completely static — all 4 summary cards ("Total Tasks", "Pending Info", "Ready to Schedule", "Active Tasks") show hardcoded zeros with no API calls. Wire up real data so the dashboard provides value as the landing page.

## Status
Not Started

## Subtasks
- Add data-fetching hooks to `DashboardPage.tsx` (`frontend/src/pages/DashboardPage.tsx`):
  - Use `useQuery` (or `useEffect` + `useState`) to call:
    - `api.tickets.listActive()` → extract `total` for "Active Tasks" card
    - `api.missingInfo.list()` → count items for "Pending Info" card
    - `api.scheduling.list()` → count items for "Ready to Schedule" card
    - Total count = sum of above + any other statuses for "Total Tasks" card
  - Show loading skeletons while fetching
  - Show error state with retry if any call fails
- Make summary cards clickable — each card navigates to its respective page:
  - "Total Tasks" → `/active-tasks`
  - "Pending Info" → `/missing-info`
  - "Ready to Schedule" → `/scheduling`
  - "Active Tasks" → `/active-tasks`
- Add LLM health indicator:
  - Call `api.llm.health()` on mount
  - Show a small status badge: green "Online" / red "Offline" / yellow "Loading..."
  - Display current model name from health response
- Add recent activity section (optional, stretch goal):
  - Call `api.aiLogs.list({ limit: 5 })` to show 5 most recent AI actions
  - Each row shows: timestamp, action type, ticket subject, success/fail badge
- Write tests:
  - Dashboard renders loading state
  - Dashboard renders cards with real data
  - Cards are clickable and navigate correctly
  - LLM health badge shows correct status

## Dependencies
None

## Acceptance Criteria
- Dashboard shows real counts for all 4 summary cards
- Cards are clickable and navigate to the correct pages
- LLM health indicator shows current status
- Loading and error states are handled gracefully
- All existing tests pass
