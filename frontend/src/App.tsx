import { BrowserRouter, Route, Routes } from "react-router-dom"
import { Layout } from "@/components/Layout"
import { DashboardPage } from "@/pages/DashboardPage"
import { MissingInfoPage } from "@/pages/MissingInfoPage"
import { SchedulingPage } from "@/pages/SchedulingPage"
import { ActiveTasksPage } from "@/pages/ActiveTasksPage"
import { TaskDetail } from "@/pages/TaskDetail"
import { AiLogsPage } from "@/pages/AiLogsPage"
import { ErrorBoundary } from "@/components/ErrorBoundary"

function App() {
  return (
    <BrowserRouter>
      <ErrorBoundary>
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
              path="ai-logs"
              element={
                <ErrorBoundary fallbackTitle="AI Logs Error">
                  <AiLogsPage />
                </ErrorBoundary>
              }
            />
          </Route>
        </Routes>
      </ErrorBoundary>
    </BrowserRouter>
  )
}

export default App
