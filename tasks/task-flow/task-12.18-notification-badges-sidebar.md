# Task 12.18 — Notification Badges on Sidebar

## Description
The sidebar navigation shows 5 links but no indication of how many items are in each queue. Users must click through to each page to check for pending items. Add notification badges that show queue counts at a glance.

## Status
Not Started

## Subtasks
- Add badge counts to `Layout.tsx` (`frontend/src/components/Layout.tsx`):
  - On layout mount (and on 30-second interval), fetch queue counts:
    - `api.missingInfo.list()` → count items → badge on "Missing Info" nav
    - `api.scheduling.list()` → count items → badge on "Scheduling" nav
    - `api.tickets.listActive({ limit: 1 })` → use `total` → badge on "Active Tasks" nav
  - Show badge only if count > 0
  - Use a small pill badge (number in a circle) next to the nav label
- Add badge colors:
  - Missing Info: yellow/amber badge
  - Scheduling: blue badge
  - Active Tasks: green badge (only if count > 0, hidden otherwise to reduce noise)
- Add a `useQueueCounts()` hook (`frontend/src/hooks/useQueueCounts.ts`):
  - Encapsulates the fetching logic
  - Returns `{ missingInfoCount, schedulingCount, activeCount, isLoading }`
  - Used by Layout.tsx
- Write tests:
  - Badge shows correct count
  - Badge hidden when count is 0
  - Badge updates on interval refresh

## Dependencies
None

## Acceptance Criteria
- Sidebar shows badge counts for Missing Info and Scheduling queues
- Badges update automatically every 30 seconds
- Badges are hidden when count is 0
- Badge colors are consistent with the queue theme
- All existing tests pass
