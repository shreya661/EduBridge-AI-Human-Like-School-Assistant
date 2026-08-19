"""Audit event contracts for future persistent security auditing."""

from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, Field

from app.authz.guard import AuthorizationReason
from app.nlu.intents import Intent
from app.session.models import Role


class AuditEvent(BaseModel):
    """A secret-free record of an authorization decision."""

    model_config = ConfigDict(frozen=True)

    user_id: str
    role: Role
    intent: Intent
    allowed: bool
    reason: AuthorizationReason
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
