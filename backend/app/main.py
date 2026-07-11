from fastapi import FastAPI

app = FastAPI(
    title="AI Task Manager",
    description="Local-first AI task management assistant",
    version="0.1.0",
)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
