"""Tool interface for escalating requests to human teachers or school management."""

from typing import Dict, Any, Optional
from app.mock_api.escalation import escalation_service, EscalationTicket, EscalationStatus
from app.session.models import Identity
from app.security.audit_log import audit_logger


class EscalationTool:
    """Escalate queries to human teachers or administrators."""

    def __init__(self):
        self.service = escalation_service

    def execute(
        self,
        identity: Identity,
        target: str = "teacher",
        reason: str = "Requesting callback from staff",
        student_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute escalation with audit logging and return verifiable result."""
        ticket: EscalationTicket = self.service.create_escalation(
            requester_id=identity.user_id,
            requester_role=identity.role.value,
            target=target,
            reason=reason,
            student_id=student_id or identity.student_id
        )

        audit_logger.record_event(
            user_id=identity.user_id,
            role=identity.role.value,
            intent=f"escalate_to_{ticket.target.value}",
            allowed=True,
            reason="AUTHORIZED",
            target_resource=ticket.ticket_id,
            metadata={"ticket_id": ticket.ticket_id, "status": ticket.status.value}
        )

        return {
            "success": ticket.status == EscalationStatus.SUBMITTED,
            "status": ticket.status.value,
            "ticket_id": ticket.ticket_id,
            "target": ticket.target.value,
            "created_at": ticket.created_at,
            "contact_phone": ticket.contact_phone,
            "message": f"Escalation ticket {ticket.ticket_id} created for {ticket.target.value}. Staff will follow up shortly."
        }


# Global tool instance
escalation_tool = EscalationTool()
