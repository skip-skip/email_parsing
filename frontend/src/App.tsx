import { BrowserRouter, Route, Routes } from "react-router-dom"
import { Layout } from "@/components/Layout"
import { DashboardPage } from "@/pages/DashboardPage"
import { MissingInfoPage } from "@/pages/MissingInfoPage"
import { SchedulingPage } from "@/pages/SchedulingPage"
import { ActiveTasksPage } from "@/pages/ActiveTasksPage"
import { TaskDetail } from "@/pages/TaskDetail"
import { AiLogsPage } from "@/pages/AiLogsPage"

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<DashboardPage />} />
          <Route path="missing-info" element={<MissingInfoPage />} />
          <Route path="scheduling" element={<SchedulingPage />} />
          <Route path="active-tasks" element={<ActiveTasksPage />} />
          <Route path="active-tasks/:ticketId" element={<TaskDetail />} />
          <Route path="ai-logs" element={<AiLogsPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
