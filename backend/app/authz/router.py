# backend/app/authz/router.py
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from .guard import authorize_request
from ..session.models import Identity
from ..session.dependencies import require_authenticated_identity

router = APIRouter(prefix="/api/v1/authz", tags=["authorization"])

@router.post("/authorize")
async def authorize_endpoint(
    request_data: Dict[str, Any],
    identity: Identity = Depends(require_authenticated_identity)
) -> Dict[str, bool]:
    """
    Secure authorization endpoint that gets identity from authenticated session
    Client can no longer control their identity - it comes from the server-side session
    """
    intent = request_data.get("intent")
    target_data = request_data.get("target_data", {})
    
    if not intent:
        raise HTTPException(status_code=400, detail="intent is required")
    
    is_authorized = authorize_request(identity, intent, target_data)
    
    return {"authorized": is_authorized}
