import { useEffect, useCallback, useRef } from "react"
import { useNavigate } from "react-router-dom"

interface ShortcutMap {
  [key: string]: () => void
}

export function useKeyboardShortcuts(shortcuts: ShortcutMap) {
  const navigate = useNavigate()
  const shortcutsRef = useRef(shortcuts)
  shortcutsRef.current = shortcuts

  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (
        e.target instanceof HTMLInputElement ||
        e.target instanceof HTMLTextAreaElement ||
        e.target instanceof HTMLSelectElement ||
        (e.target as HTMLElement)?.isContentEditable
      ) {
        return
      }

      const key = [
        e.ctrlKey || e.metaKey ? "ctrl" : "",
        e.shiftKey ? "shift" : "",
        e.altKey ? "alt" : "",
        e.key.toLowerCase(),
      ]
        .filter(Boolean)
        .join("+")

      const handler = shortcutsRef.current[key]
      if (handler) {
        e.preventDefault()
        handler()
        return
      }

      const plainKey = e.key.toLowerCase()
      const plainHandler = shortcutsRef.current[plainKey]
      if (plainHandler) {
        e.preventDefault()
        plainHandler()
      }
    },
    [],
  )

  useEffect(() => {
    window.addEventListener("keydown", handleKeyDown)
    return () => window.removeEventListener("keydown", handleKeyDown)
  }, [handleKeyDown])

  return { navigate }
}
