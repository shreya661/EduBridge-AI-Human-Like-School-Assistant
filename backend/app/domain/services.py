# backend/app/domain/services.py
from typing import List, Optional
from datetime import date
from .repositories import (
    StudentRepository, ParentRepository, TeacherRepository,
    ClassRepository, ParentStudentRepository, TeacherClassRepository,
    AttendanceRepository
)
from .models import Student, Parent, Teacher, Class, AttendanceRecord


class SchoolDomainService:
    def __init__(
        self,
        student_repo: StudentRepository,
        parent_repo: ParentRepository,
        teacher_repo: TeacherRepository,
        class_repo: ClassRepository,
        parent_student_repo: ParentStudentRepository,
        teacher_class_repo: TeacherClassRepository,
        attendance_repo: AttendanceRepository
    ):
        self.student_repo = student_repo
        self.parent_repo = parent_repo
        self.teacher_repo = teacher_repo
        self.class_repo = class_repo
        self.parent_student_repo = parent_student_repo
        self.teacher_class_repo = teacher_class_repo
        self.attendance_repo = attendance_repo
    
    def get_children_for_parent(self, parent_id: str) -> List[Student]:
        """Get all students associated with a parent"""
        student_ids = self.parent_student_repo.get_children_for_parent(parent_id)
        students = []
        for student_id in student_ids:
            student = self.student_repo.get_student(student_id)
            if student:
                students.append(student)
        return students
    
    def get_classes_for_teacher(self, teacher_id: str) -> List[Class]:
        """Get all classes assigned to a teacher"""
        class_ids = self.teacher_class_repo.get_classes_for_teacher(teacher_id)
        classes = []
        for class_id in class_ids:
            class_ = self.class_repo.get_class(class_id)
            if class_:
                classes.append(class_)
        return classes
    
    def get_students_in_class(self, class_id: str) -> List[Student]:
        """Get all students in a class"""
        all_students = self.student_repo.get_all_students()
        class_students = []
        for student in all_students:
            if student.class_id == class_id:
                class_students.append(student)
        return class_students
    
    def get_attendance_for_student(self, student_id: str, date_from: Optional[date] = None, date_to: Optional[date] = None) -> List[AttendanceRecord]:
        """Get attendance records for a student"""
        return self.attendance_repo.get_attendance_by_student(student_id, date_from, date_to)
    
    def get_attendance_for_class(self, class_id: str, date_from: Optional[date] = None, date_to: Optional[date] = None) -> List[AttendanceRecord]:
        """Get attendance records for a class"""
        return self.attendance_repo.get_attendance_by_class(class_id, date_from, date_to)
    
    def record_attendance(self, student_id: str, class_id: str, date: date, status: str, recorded_by: str) -> AttendanceRecord:
        """Record attendance for a student"""
        from uuid import uuid4
        record_id = f"att-{uuid4().hex[:8]}"
        
        record = AttendanceRecord(
            record_id=record_id,
            student_id=student_id,
            class_id=class_id,
            date=date,
            status=status,
            recorded_by=recorded_by
        )
        
        return self.attendance_repo.create_attendance_record(record)

    def get_students_for_teacher(self, teacher_id: str) -> List[Student]:
        """Get all distinct students across all classes assigned to a teacher"""
        classes = self.get_classes_for_teacher(teacher_id)
        seen_ids = set()
        students = []
        for cl in classes:
            for st in self.get_students_in_class(cl.class_id):
                if st.student_id not in seen_ids:
                    seen_ids.add(st.student_id)
                    students.append(st)
        return students

    def get_all_teachers(self) -> List[Teacher]:
        """Get all teachers in the school"""
        return self.teacher_repo.get_all_teachers()

    def get_all_students(self) -> List[Student]:
        """Get all students in the school"""
        return self.student_repo.get_all_students()

    def get_all_classes(self) -> List[Class]:
        """Get all classes in the school"""
        return self.class_repo.get_all_classes()
