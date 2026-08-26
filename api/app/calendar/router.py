"""HTTP boundary for School Calendar and Class Timetables."""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, Query, HTTPException, status

from app.calendar.models import (
    CalendarEvent,
    ClassTimetable,
    CALENDAR_EVENTS,
    TIMETABLES,
    EventCategory
)
from app.session.models import Identity, Role
from app.session.dependencies import require_authenticated_identity

router = APIRouter(prefix="/api/v1/calendar", tags=["calendar"])


@router.get("/events", response_model=List[CalendarEvent])
async def list_calendar_events(
    category: Optional[str] = Query(None, description="Filter by category: exam, holiday, event, meeting, academic"),
    identity: Identity = Depends(require_authenticated_identity)
) -> List[CalendarEvent]:
    """Retrieve school calendar events filtered by category and active role clearance."""
    role_str = identity.role.value.upper() if hasattr(identity.role, "value") else str(identity.role).upper()
    
    events = [
        evt for evt in CALENDAR_EVENTS
        if role_str in evt.applicable_roles
    ]

    if category and category.lower() != "all":
        events = [evt for evt in events if evt.category.value.lower() == category.lower()]

    return events


@router.get("/timetable/{class_id}", response_model=ClassTimetable)
async def get_class_timetable(
    class_id: str,
    identity: Identity = Depends(require_authenticated_identity)
) -> ClassTimetable:
    """Retrieve period-by-period class timetable."""
    norm_id = class_id.strip().upper()
    if norm_id not in TIMETABLES:
        # Fallback to 10-A
        norm_id = "10-A"

    return TIMETABLES[norm_id]


@router.get("/summary")
async def get_calendar_summary(
    identity: Identity = Depends(require_authenticated_identity)
) -> Dict[str, Any]:
    """Return top 3 upcoming calendar items and current day schedule snippet."""
    role_str = identity.role.value.upper() if hasattr(identity.role, "value") else str(identity.role).upper()
    relevant_events = [evt for evt in CALENDAR_EVENTS if role_str in evt.applicable_roles][:3]

    return {
        "success": True,
        "upcoming_count": len(CALENDAR_EVENTS),
        "next_event": relevant_events[0].model_dump() if relevant_events else None,
        "upcoming_events": [evt.model_dump() for evt in relevant_events],
        "default_class": "10-A"
    }
