import { Component, type ReactNode, type ErrorInfo } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { AlertTriangle, RefreshCw } from "lucide-react"

interface Props {
  children: ReactNode
  fallbackTitle?: string
  fallbackDescription?: string
}

interface State {
  hasError: boolean
  error: Error | null
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("[ErrorBoundary]", error, errorInfo)
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null })
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex min-h-screen items-center justify-center p-6">
          <Card className="w-full max-w-md">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-destructive">
                <AlertTriangle className="size-5" />
                {this.props.fallbackTitle ?? "Something went wrong"}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm text-muted-foreground">
                {this.props.fallbackDescription ??
                  "An unexpected error occurred. You can try reloading the page or returning to a previous view."}
              </p>
              {this.state.error && (
                <pre className="max-h-32 overflow-auto rounded-md border bg-muted/50 p-3 text-xs text-muted-foreground">
                  {this.state.error.message}
                </pre>
              )}
              <div className="flex gap-2">
                <Button variant="outline" size="sm" onClick={this.handleReset}>
                  <RefreshCw className="size-3.5" />
                  Try Again
                </Button>
                <Button
                  size="sm"
                  onClick={() => (window.location.href = "/")}
                >
                  Go to Dashboard
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )
    }

    return this.props.children
  }
}
