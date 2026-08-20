# backend/app/main.py
from fastapi import FastAPI, Depends, HTTPException
from typing import Dict, Any
import uvicorn
from app.session.models import Identity, Role
from app.session.dependencies import require_authenticated_identity
from app.authz.router import router as authz_router
from app.session.store import identity_store
from app.auth.router import router as auth_router
from app.conversation.router import router as assistant_router, conversation_router
from app.nlu.router import router as nlu_router
from app.attendance.router import router as attendance_router
from app.domain.seed_data import seed_school_data

app = FastAPI(title="XYZ AI - Human-Like AI School Assistant")


@app.on_event("startup")
def startup_event():
    """Initialize domain data on startup"""
    seed_school_data()


@app.get("/health")
def health_check() -> Dict[str, str]:
    return {"status": "ok", "service": "XYZ AI"}


@app.get("/api/v1/users/{user_id}")
async def get_user_info(user_id: str, identity: Identity = Depends(require_authenticated_identity)):
    """Secure endpoint - identity comes from authenticated session, not path"""
    if identity.user_id != user_id and identity.role not in [Role.TEACHER, Role.PRINCIPAL]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    requested_identity = identity_store.get_identity(user_id)
    if not requested_identity:
        raise HTTPException(status_code=404, detail="User not found")
    
    return requested_identity.model_dump()


from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from app.mock_api.escalation_router import router as escalation_router
from app.voice.router import router as voice_router
from app.avatar.router import router as avatar_router

# Include all core service routers
app.include_router(auth_router)
app.include_router(authz_router)
app.include_router(attendance_router)
app.include_router(nlu_router)
app.include_router(assistant_router)
app.include_router(conversation_router)
app.include_router(escalation_router)
app.include_router(voice_router)
app.include_router(avatar_router)

# Mount static directory for interactive frontend
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    @app.get("/")
    async def serve_index():
        return FileResponse(os.path.join(static_dir, "index.html"))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
