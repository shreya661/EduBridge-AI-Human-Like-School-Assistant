from .schemas import Attendance
from ..mock_api.attendance import get_student_attendance, get_class_attendance, get_school_attendance

class AttendanceService:
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