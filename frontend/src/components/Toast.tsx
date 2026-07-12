import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
} from "react"
import type { ReactNode } from "react"
import { cn } from "@/lib/utils"
import { CheckCircle, AlertCircle, Info, X } from "lucide-react"

type ToastType = "success" | "error" | "info"

interface Toast {
  id: number
  type: ToastType
  message: string
}

interface ToastContextValue {
  toast: (type: ToastType, message: string) => void
}

const ToastContext = createContext<ToastContextValue | null>(null)

let toastId = 0

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([])
  const timerRef = useRef<Map<number, ReturnType<typeof setTimeout>>>(new Map())

  const removeToast = useCallback((id: number) => {
    setToasts((prev) => prev.filter((t) => t.id !== id))
    const timer = timerRef.current.get(id)
    if (timer) {
      clearTimeout(timer)
      timerRef.current.delete(id)
    }
  }, [])

  const toast = useCallback(
    (type: ToastType, message: string) => {
      const id = ++toastId
      setToasts((prev) => [...prev.slice(-4), { id, type, message }])
      const timer = setTimeout(() => removeToast(id), 4000)
      timerRef.current.set(id, timer)
    },
    [removeToast],
  )

  useEffect(() => {
    const timers = timerRef.current
    return () => {
      for (const timer of timers.values()) {
        clearTimeout(timer)
      }
    }
  }, [])

  return (
    <ToastContext.Provider value={{ toast }}>
      {children}
      <div className="pointer-events-none fixed bottom-4 right-4 z-[100] flex flex-col-reverse gap-2 sm:bottom-6 sm:right-6">
        {toasts.map((t) => (
          <ToastItem key={t.id} toast={t} onDismiss={() => removeToast(t.id)} />
        ))}
      </div>
    </ToastContext.Provider>
  )
}

export function useToast() {
  const ctx = useContext(ToastContext)
  if (!ctx) throw new Error("useToast must be used within a ToastProvider")
  return ctx
}

const icons: Record<ToastType, typeof CheckCircle> = {
  success: CheckCircle,
  error: AlertCircle,
  info: Info,
}

const styles: Record<ToastType, string> = {
  success:
    "border-green-200 bg-green-50 text-green-800 dark:border-green-800 dark:bg-green-950 dark:text-green-200",
  error:
    "border-red-200 bg-red-50 text-red-800 dark:border-red-800 dark:bg-red-950 dark:text-red-200",
  info:
    "border-blue-200 bg-blue-50 text-blue-800 dark:border-blue-800 dark:bg-blue-950 dark:text-blue-200",
}

function ToastItem({ toast: t, onDismiss }: { toast: Toast; onDismiss: () => void }) {
  const Icon = icons[t.type]

  return (
    <div
      className={cn(
        "pointer-events-auto flex items-start gap-3 rounded-lg border px-4 py-3 shadow-lg transition-all animate-in slide-in-from-bottom-5 fade-in duration-300",
        styles[t.type],
      )}
    >
      <Icon className="mt-0.5 size-4 shrink-0" />
      <p className="flex-1 text-sm font-medium">{t.message}</p>
      <button
        type="button"
        onClick={onDismiss}
        className="shrink-0 rounded-md p-0.5 opacity-60 transition-opacity hover:opacity-100"
      >
        <X className="size-3.5" />
      </button>
    </div>
  )
}
