"""HTTP boundary for Role Guidance and Capability Documentation."""

from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query

from app.domain.role_guides import ROLE_GUIDES_DATA, RoleCapabilityGuide
from app.session.models import Identity
from app.session.dependencies import require_authenticated_identity

router = APIRouter(prefix="/api/v1/role-guides", tags=["role-guides"])


@router.get("", response_model=Dict[str, RoleCapabilityGuide])
async def get_all_role_guides(
    identity: Identity = Depends(require_authenticated_identity)
) -> Dict[str, RoleCapabilityGuide]:
    """Retrieve capabilities and RBAC security boundaries for all roles."""
    return ROLE_GUIDES_DATA


@router.get("/active", response_model=RoleCapabilityGuide)
async def get_active_role_guide(
    identity: Identity = Depends(require_authenticated_identity)
) -> RoleCapabilityGuide:
    """Retrieve role guidance specifically for the caller's active role."""
    role_key = identity.role.value.upper() if hasattr(identity.role, "value") else str(identity.role).upper()
    if role_key not in ROLE_GUIDES_DATA:
        raise HTTPException(status_code=404, detail="Role guide not found")
    return ROLE_GUIDES_DATA[role_key]
