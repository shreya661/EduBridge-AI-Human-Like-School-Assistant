# backend/app/auth/router.py
from fastapi import APIRouter, Depends, HTTPException, Response, Request
from typing import Dict, Any
from pydantic import BaseModel
from ..session.models import Identity, Role
from ..session.store import identity_store
from ..session.session_manager import session_store
from ..session.dependencies import require_authenticated_identity


class LoginRequest(BaseModel):
    user_id: str


class LoginResponse(BaseModel):
    user: Dict[str, Any]


class CurrentUserResponse(BaseModel):
    user: Dict[str, Any]


router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])

@router.post("/login", response_model=LoginResponse)
async def login(response: Response, login_request: LoginRequest) -> LoginResponse:
    """Development login endpoint - validates user_id against trusted store"""
    identity = identity_store.get_identity(login_request.user_id)
    if not identity:
        raise HTTPException(status_code=401, detail="Invalid user_id")
    
    # Create secure session
    session_id = session_store.create_session(identity)
    
    # Set HttpOnly cookie for session
    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax",
        max_age=3600  # 1 hour
    )
    
    # Return safe user information
    return LoginResponse(
        user={
            "user_id": identity.user_id,
            "role": identity.role.value.lower(),
            "name": identity.name
        }
    )


@router.get("/me", response_model=CurrentUserResponse)
async def get_current_user(identity: Identity = Depends(require_authenticated_identity)) -> CurrentUserResponse:
    """Get current authenticated user info from session"""
    return CurrentUserResponse(
        user={
            "user_id": identity.user_id,
            "role": identity.role.value.lower(),
            "name": identity.name
        }
    )


@router.post("/logout")
async def logout(request: Request, response: Response) -> Dict[str, str]:
    """Logout endpoint - invalidates current session"""
    session_id = None
    
    # Try header first
    session_header = request.headers.get("X-Session-ID")
    if session_header:
        session_id = session_header
    else:
        # Try cookie
        session_cookie = request.cookies.get("session_id")
        if session_cookie:
            session_id = session_cookie
    
    if not session_id:
        raise HTTPException(status_code=401, detail="No session provided")
    
    # Validate session exists (this will also clean up expired sessions)
    session_data = session_store.get_session(session_id)
    if not session_data:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    
    # Invalidate the session
    session_store.invalidate_session(session_id)
    
    # Clear the cookie
    response.delete_cookie("session_id")
    
    return {"message": "Logged out successfully"}
