# backend/app/attendance/models.py
from pydantic import BaseModel
from datetime import date
from typing import Optional
from enum import Enum

class AttendanceStatus(str, Enum):
    PRESENT = "PRESENT"
    ABSENT = "ABSENT"
    LATE = "LATE"
    EXCUSED = "EXCUSED"

class AttendanceRecord(BaseModel):
    record_id: str
    student_id: str
    date: date
    status: AttendanceStatus
    recorded_by: str  # user_id of who recorded it
    created_at: Optional[date] = None
