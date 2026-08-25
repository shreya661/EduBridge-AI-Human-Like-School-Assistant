"""HTTP boundary for School Analytics and Dashboard Data."""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, Query

from app.mock_api.analytics import analytics_service
from app.session.models import Identity, Role
from app.session.dependencies import require_authenticated_identity
from app.security.audit_log import audit_logger

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])


@router.get("/overview")
async def get_analytics_overview(
    identity: Identity = Depends(require_authenticated_identity)
) -> Dict[str, Any]:
    """Retrieve comprehensive school analytics overview including pie chart distribution."""
    data = analytics_service.get_school_attendance_summary()
    
    total = data["total_students"]
    present = data["present_today"]
    absent = data["absent_today"]
    late = 12
    excused = 8
    
    # Calculate pie chart slice percentages
    pie_distribution = [
        {"label": "Present", "count": present - late, "pct": round(((present - late) / total) * 100, 1), "color": "#10b981"},
        {"label": "Late", "count": late, "pct": round((late / total) * 100, 1), "color": "#f59e0b"},
        {"label": "Excused", "count": excused, "pct": round((excused / total) * 100, 1), "color": "#6366f1"},
        {"label": "Unexcused Absent", "count": absent - excused, "pct": round(((absent - excused) / total) * 100, 1), "color": "#ef4444"},
    ]

    monthly_trend = [
        {"month": "May", "attendance_pct": 91.2},
        {"month": "Jun", "attendance_pct": 93.0},
        {"month": "Jul", "attendance_pct": 94.5},
        {"month": "Aug", "attendance_pct": 92.4},
    ]

    audit_logger.record_event(
        user_id=identity.user_id,
        role=identity.role.value,
        intent="view_school_analytics",
        allowed=True,
        reason="AUTHORIZED",
        target_resource="DASHBOARD_ANALYTICS"
    )

    return {
        "success": True,
        "kpis": {
            "overall_attendance_pct": data["overall_attendance_pct"],
            "total_students": total,
            "present_today": present,
            "absent_today": absent,
            "flagged_count": len(data["flagged_students"]),
            "classes_tracked": len(data["by_class"])
        },
        "pie_distribution": pie_distribution,
        "by_class": data["by_class"],
        "monthly_trend": monthly_trend,
        "flagged_students": data["flagged_students"]
    }


@router.get("/flagged")
async def get_flagged_students(
    identity: Identity = Depends(require_authenticated_identity)
) -> Dict[str, Any]:
    """Retrieve students with low attendance requiring administrative follow-up."""
    data = analytics_service.get_school_attendance_summary()
    return {
        "success": True,
        "flagged_students": data["flagged_students"],
        "threshold_pct": 75.0
    }
