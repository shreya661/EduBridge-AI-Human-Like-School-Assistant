# backend/app/attendance/router.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from datetime import date
from .models import AttendanceRecord, AttendanceStatus
from .service import attendance_service
from ..session.models import Identity
from ..session.dependencies import require_authenticated_identity

router = APIRouter(prefix="/api/v1/attendance", tags=["attendance"])

@router.get("/student/{student_id}", response_model=List[AttendanceRecord])
async def get_student_attendance(
    student_id: str,
    identity: Identity = Depends(require_authenticated_identity)
) -> List[AttendanceRecord]:
    """
    Get attendance for a specific student with authorization enforcement
    """
    try:
        records = attendance_service.get_attendance_by_student(student_id, identity)
        return records
    except HTTPException:
        # Re-raise HTTP exceptions from service
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/record")
async def record_attendance(
    student_id: str,
    class_id: str,
    date: date,
    status: AttendanceStatus,
    identity: Identity = Depends(require_authenticated_identity)
) -> AttendanceRecord:
    """
    Record attendance with authorization enforcement
    """
    try:
        record = attendance_service.record_attendance(
            student_id=student_id,
            class_id=class_id,
            date=date,
            status=status,
            recorded_by=identity.user_id,
            identity=identity
        )
        return record
    except HTTPException:
        # Re-raise HTTP exceptions from service
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
