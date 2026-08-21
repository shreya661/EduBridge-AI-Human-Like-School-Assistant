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
    """Secure endpoint with strict role scoping:
    - Student: Can only view their own profile.
    - Teacher: Can view their own profile and students enrolled in their assigned classes.
    - Parent: Can view their linked children.
    - Principal: Full access to all teachers, students, and self.
    """
    from app.domain import school_domain_service

    # 1. Self access is always permitted
    if identity.user_id == user_id:
        requested = identity_store.get_identity(user_id)
        if not requested:
            raise HTTPException(status_code=404, detail="User not found")
        return requested.model_dump()

    # 2. Student: Strictly self-only
    if identity.role == Role.STUDENT:
        raise HTTPException(
            status_code=403,
            detail="Students are restricted to viewing only their own profile."
        )

    # 3. Parent: Linked children only
    if identity.role == Role.PARENT:
        children = school_domain_service.get_children_for_parent(identity.user_id)
        if user_id not in [c.student_id for c in children]:
            raise HTTPException(
                status_code=403,
                detail="Parents can only access profiles of their linked children."
            )
        requested = identity_store.get_identity(user_id)
        return requested.model_dump() if requested else {"user_id": user_id}

    # 4. Teacher: Self + Students in assigned classes
    if identity.role == Role.TEACHER:
        assigned_students = school_domain_service.get_students_for_teacher(identity.user_id)
        if user_id not in [s.student_id for s in assigned_students]:
            raise HTTPException(
                status_code=403,
                detail="Teachers are restricted to viewing students enrolled in their assigned classes."
            )
        requested = identity_store.get_identity(user_id)
        return requested.model_dump() if requested else {"user_id": user_id}

    # 5. Principal: Unrestricted institutional access
    if identity.role == Role.PRINCIPAL:
        requested = identity_store.get_identity(user_id)
        if not requested:
            raise HTTPException(status_code=404, detail="User not found")
        return requested.model_dump()

    raise HTTPException(status_code=403, detail="Access denied")


from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from app.mock_api.escalation_router import router as escalation_router
from app.voice.router import router as voice_router
from app.avatar.router import router as avatar_router
from app.directory.router import router as directory_router

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
app.include_router(directory_router)

# Mount static directory for interactive frontend
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    @app.get("/")
    async def serve_index():
        return FileResponse(os.path.join(static_dir, "index.html"))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
