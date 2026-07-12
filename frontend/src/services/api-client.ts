import axios from "axios"
import type { InternalAxiosRequestConfig } from "axios"

interface RequestMetadata {
  startTime: number
}

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000",
  headers: {
    "Content-Type": "application/json",
  },
})

apiClient.interceptors.request.use((config: InternalAxiosRequestConfig & { metadata?: RequestMetadata }) => {
  config.metadata = { startTime: Date.now() }
  return config
})

apiClient.interceptors.response.use(
  (response) => {
    const cfg = response.config as InternalAxiosRequestConfig & { metadata?: RequestMetadata }
    const duration = Date.now() - (cfg.metadata?.startTime ?? 0)
    console.debug(`[API] ${response.config.method?.toUpperCase()} ${response.config.url} → ${response.status} (${duration}ms)`)
    return response
  },
  (error) => {
    console.error("API Error:", error.response?.data ?? error.message)
    return Promise.reject(error)
  },
)

export default apiClient
