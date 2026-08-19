"""FastAPI application entry point for XYZ AI."""

from fastapi import FastAPI

from app.authz.router import router as authz_router
from app.conversation.router import router as conversation_router
from app.nlu.router import router as nlu_router


app = FastAPI(
    title="XYZ AI",
    description="Human-Like AI School Assistant",
    version="0.1.0",
)

app.include_router(nlu_router)
app.include_router(authz_router)
app.include_router(conversation_router)


@app.get("/health")
def health_check() -> dict[str, str]:
    """Return the service health status."""
    return {"status": "ok", "service": "XYZ AI"}
