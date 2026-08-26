# backend/app/attendance/service.py
from typing import List, Optional
from datetime import date
from fastapi import HTTPException
from app.session.models import Identity, Role
from .models import AttendanceRecord, AttendanceStatus
from .schemas import Attendance
from ..domain import attendance_repo, school_domain_service
from ..mock_api.attendance import get_student_attendance, get_class_attendance, get_school_attendance


class MockAttendanceService:
    def __init__(self):
        # Initialize with domain service
        self.attendance_repository = attendance_repo
    
    def get_attendance_by_student(self, student_id: str, identity: Optional[Identity] = None) -> List[AttendanceRecord]:
        if identity:
            from app.authz.ownership import validate_ownership
            if not validate_ownership(identity, student_id):
                raise HTTPException(status_code=403, detail="Access denied to student attendance")
        return self.attendance_repository.get_attendance_by_student(student_id)
    
    def record_attendance(
        self,
        student_id: str,
        class_id: str,
        date: date,
        status: AttendanceStatus,
        recorded_by: str,
        identity: Optional[Identity] = None
    ) -> AttendanceRecord:
        if identity:
            from app.authz.ownership import validate_ownership
            if identity.role not in [Role.TEACHER, Role.PRINCIPAL]:
                raise HTTPException(status_code=403, detail="Only teachers or principals can record attendance")
            if not validate_ownership(identity, student_id):
                raise HTTPException(status_code=403, detail="Access denied to record attendance for student")
        return school_domain_service.record_attendance(student_id, class_id, date, status, recorded_by)

    def get_student_attendance(self, student_id: int) -> Attendance:
        data = get_student_attendance(student_id)
        if data:
            return Attendance(**data)
        else:
            raise ValueError("Student not found")

    def get_class_attendance(self, class_id: int) -> list[Attendance]:
        data = get_class_attendance(class_id)
        if data:
            return [Attendance(**student) for student in data]
        else:
            raise ValueError("Class not found")

    def get_school_attendance(self) -> list[Attendance]:
        data = get_school_attendance()
        if data:
            return [Attendance(**student) for student in data]
        else:
            raise ValueError("School attendance data not found")

    def mark_attendance(self, student_id: int, present: bool) -> str:
        return "Not implemented in Phase 4"


# Global instance
attendance_service = MockAttendanceService()
AttendanceService = MockAttendanceService
AuthorizedAttendanceService = MockAttendanceService