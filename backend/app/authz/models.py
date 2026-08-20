# backend/app/authz/models.py
from pydantic import BaseModel
from enum import Enum
from typing import Optional
from ..session.models import Identity


class AuthorizationDecision(str, Enum):
    ALLOWED = "ALLOWED"
    DENIED = "DENIED"


class AuthorizationResult(BaseModel):
    decision: AuthorizationDecision
    allowed: bool
    reason: str = ""
    user_id: str
    role: str
    operation: str
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    timestamp: str


class ResourceTarget(BaseModel):
    resource_type: str
    resource_id: str
    sub_resource_id: Optional[str] = None
