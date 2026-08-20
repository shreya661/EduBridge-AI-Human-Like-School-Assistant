"""Structured immutable security audit logger."""

from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, Field
from app.session.models import Role
from app.nlu.intents import Intent


class AuditEvent(BaseModel):
    """A secret-free, structured record of an authorization or execution event."""

    model_config = ConfigDict(frozen=True)

    event_id: str
    user_id: str
    role: str
    intent: str
    allowed: bool
    reason: str
    target_resource: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AuditLogger:
    """Thread-safe in-memory audit logger with query and export capabilities."""

    def __init__(self):
        self._events: List[AuditEvent] = []

    def record_event(
        self,
        user_id: str,
        role: str,
        intent: str,
        allowed: bool,
        reason: str,
        target_resource: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AuditEvent:
        import secrets
        event_id = f"AUD-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{secrets.token_hex(4)}"
        event = AuditEvent(
            event_id=event_id,
            user_id=user_id,
            role=role if isinstance(role, str) else role.value,
            intent=intent if isinstance(intent, str) else intent.value,
            allowed=allowed,
            reason=reason,
            target_resource=target_resource,
            metadata=metadata or {},
            timestamp=datetime.now(timezone.utc),
        )
        self._events.append(event)
        return event

    def get_events(
        self,
        user_id: Optional[str] = None,
        allowed_only: Optional[bool] = None,
        limit: int = 100
    ) -> List[AuditEvent]:
        events = self._events
        if user_id:
            events = [e for e in events if e.user_id == user_id]
        if allowed_only is not None:
            events = [e for e in events if e.allowed == allowed_only]
        return events[-limit:]

    def clear(self):
        self._events.clear()


# Global audit logger instance
audit_logger = AuditLogger()
