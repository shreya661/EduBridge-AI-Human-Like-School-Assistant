"""Attendance tool that delegates to the Phase 4 service after authorization."""

from app.attendance.service import AttendanceService
from app.mock_api.attendance import identity_student_ids
from app.session.models import Identity

class AttendanceTool:
    def __init__(self):
        self.attendance_service = AttendanceService()

    def get_student_attendance(self, student_id: str) -> dict:
        """Return verified attendance for a trusted, already-authorized student ID."""
        school_student_id = identity_student_ids.get(student_id)
        if school_student_id is None:
            raise ValueError("Student not found")
        return self.attendance_service.get_student_attendance(school_student_id).model_dump()

    def view_own_attendance(self, identity: Identity) -> dict:
        if identity.student_id is None:
            raise ValueError("Student identity has no linked school record")
        return self.get_student_attendance(identity.student_id)

    def view_child_attendance(self, student_id: str) -> dict:
        return self.get_student_attendance(student_id)

    def view_school_attendance(self) -> list[dict]:
        attendance = self.attendance_service.get_school_attendance()
        return [record.model_dump() for record in attendance]
