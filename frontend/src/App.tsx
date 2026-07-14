import { Suspense, lazy } from "react"
import { BrowserRouter, Route, Routes } from "react-router-dom"
import { Layout } from "@/components/Layout"
import { ErrorBoundary } from "@/components/ErrorBoundary"
import { Skeleton } from "@/components/ui/skeleton"

const DashboardPage = lazy(() => import("@/pages/DashboardPage").then(m => ({ default: m.DashboardPage })))
const MissingInfoPage = lazy(() => import("@/pages/MissingInfoPage").then(m => ({ default: m.MissingInfoPage })))
const SchedulingPage = lazy(() => import("@/pages/SchedulingPage").then(m => ({ default: m.SchedulingPage })))
const ActiveTasksPage = lazy(() => import("@/pages/ActiveTasksPage").then(m => ({ default: m.ActiveTasksPage })))
const ClosedTasksPage = lazy(() => import("@/pages/ClosedTasks").then(m => ({ default: m.ClosedTasks })))
const TaskDetail = lazy(() => import("@/pages/TaskDetail").then(m => ({ default: m.TaskDetail })))
const AiLogsPage = lazy(() => import("@/pages/AiLogsPage").then(m => ({ default: m.AiLogsPage })))

function PageLoader() {
  return (
    <div className="space-y-6 p-6">
      <Skeleton className="h-8 w-48" />
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Skeleton className="h-28" />
        <Skeleton className="h-28" />
        <Skeleton className="h-28" />
        <Skeleton className="h-28" />
      </div>
      <Skeleton className="h-48" />
    </div>
  )
}

function App() {
  return (
    <BrowserRouter>
      <ErrorBoundary>
        <Suspense fallback={<PageLoader />}>
          <Routes>
            <Route element={<Layout />}>
              <Route
                index
                element={
                  <ErrorBoundary fallbackTitle="Dashboard Error">
                    <DashboardPage />
                  </ErrorBoundary>
                }
              />
              <Route
                path="missing-info"
                element={
                  <ErrorBoundary fallbackTitle="Missing Info Error">
                    <MissingInfoPage />
                  </ErrorBoundary>
                }
              />
              <Route
                path="scheduling"
                element={
                  <ErrorBoundary fallbackTitle="Scheduling Error">
                    <SchedulingPage />
                  </ErrorBoundary>
                }
              />
              <Route
                path="active-tasks"
                element={
                  <ErrorBoundary fallbackTitle="Active Tasks Error">
                    <ActiveTasksPage />
                  </ErrorBoundary>
                }
              />
              <Route
                path="active-tasks/:ticketId"
                element={
                  <ErrorBoundary fallbackTitle="Task Detail Error">
                    <TaskDetail />
                  </ErrorBoundary>
                }
              />
              <Route
                path="closed-tasks"
                element={
                  <ErrorBoundary fallbackTitle="Closed Tasks Error">
                    <ClosedTasksPage />
                  </ErrorBoundary>
                }
              />
              <Route
                path="ai-logs"
                element={
                  <ErrorBoundary fallbackTitle="AI Logs Error">
                    <AiLogsPage />
                  </ErrorBoundary>
                }
              />
            </Route>
          </Routes>
        </Suspense>
      </ErrorBoundary>
    </BrowserRouter>
  )
}

export default App
