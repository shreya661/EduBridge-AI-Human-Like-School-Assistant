"""Mock Escalation API and Ticket Management Service."""

from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime, timezone
from pydantic import BaseModel, Field
import secrets


class EscalationStatus(str, Enum):
    PENDING = "pending"
    SUBMITTED = "submitted"
    FAILED = "failed"
    CANCELLED = "cancelled"


class EscalationTarget(str, Enum):
    TEACHER = "teacher"
    MANAGEMENT = "management"


class EscalationTicket(BaseModel):
    ticket_id: str
    requester_id: str
    requester_role: str
    target: EscalationTarget
    reason: str
    student_id: Optional[str] = None
    status: EscalationStatus = EscalationStatus.SUBMITTED
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    contact_phone: Optional[str] = "+91 98765 43210"
    resolution_notes: Optional[str] = None


class MockEscalationService:
    """Mock ERP escalation and callback service."""

    def __init__(self):
        self._tickets: Dict[str, EscalationTicket] = {}

    def create_escalation(
        self,
        requester_id: str,
        requester_role: str,
        target: str,
        reason: str,
        student_id: Optional[str] = None,
    ) -> EscalationTicket:
        """Create a new human escalation ticket and return status."""
        target_enum = EscalationTarget.MANAGEMENT if "management" in target.lower() else EscalationTarget.TEACHER
        
        # Deterministic ticket ID
        rand_suffix = secrets.token_hex(3).upper()
        ticket_id = f"ESC-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{rand_suffix}"

        ticket = EscalationTicket(
            ticket_id=ticket_id,
            requester_id=requester_id,
            requester_role=requester_role,
            target=target_enum,
            reason=reason or "General query / Human intervention requested",
            student_id=student_id,
            status=EscalationStatus.SUBMITTED,
            created_at=datetime.now(timezone.utc).isoformat()
        )
        self._tickets[ticket_id] = ticket
        return ticket

    def get_ticket(self, ticket_id: str) -> Optional[EscalationTicket]:
        return self._tickets.get(ticket_id)

    def list_tickets_for_user(self, user_id: str) -> List[EscalationTicket]:
        return [t for t in self._tickets.values() if t.requester_id == user_id]

    def clear(self):
        self._tickets.clear()


# Global instance
escalation_service = MockEscalationService()
