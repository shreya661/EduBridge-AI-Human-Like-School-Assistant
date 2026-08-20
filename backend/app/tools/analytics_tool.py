"""Tool interface for school analytics queries by Principal/Management."""

from typing import Dict, Any
from app.mock_api.analytics import analytics_service
from app.session.models import Identity
from app.security.audit_log import audit_logger


class AnalyticsTool:
    """School-wide metrics and analytics retrieval."""

    def __init__(self):
        self.service = analytics_service

    def execute(self, identity: Identity) -> Dict[str, Any]:
        data = self.service.get_school_attendance_summary()
        
        audit_logger.record_event(
            user_id=identity.user_id,
            role=identity.role.value,
            intent="view_school_analytics",
            allowed=True,
            reason="AUTHORIZED",
            target_resource="SCHOOL_ANALYTICS",
            metadata={"overall_pct": data["overall_attendance_pct"]}
        )

        return {
            "success": True,
            "data": data,
            "message": f"School attendance average is {data['overall_attendance_pct']}%. Total students: {data['total_students']}."
        }


analytics_tool = AnalyticsTool()
