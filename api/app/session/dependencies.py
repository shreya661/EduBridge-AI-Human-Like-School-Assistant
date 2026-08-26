# backend/app/session/dependencies.py
from fastapi import Header, Cookie, HTTPException, Depends
from typing import Optional
from .models import Identity
from .session_manager import session_store


async def require_authenticated_identity(
    x_session_id: Optional[str] = Header(None, alias="X-Session-ID"),
    session_id: Optional[str] = Cookie(None)
) -> Identity:
    token = x_session_id or session_id
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    session_data = session_store.get_session(token)
    if not session_data:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    
    return session_data.identity


async def get_current_session(
    x_session_id: Optional[str] = Header(None, alias="X-Session-ID"),
    session_id: Optional[str] = Cookie(None)
):
    token = x_session_id or session_id
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    session_data = session_store.get_session(token)
    if not session_data:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    
    return session_data

