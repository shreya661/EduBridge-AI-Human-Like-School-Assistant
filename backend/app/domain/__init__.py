# backend/app/domain/__init__.py
from datetime import date
from .models import (
    Student, Parent, Teacher, Class,
    ParentStudent, TeacherClass, AttendanceRecord, AttendanceStatus, UserRole
)
from .repositories import (
    StudentRepository, ParentRepository, TeacherRepository,
    ClassRepository, ParentStudentRepository, TeacherClassRepository,
    AttendanceRepository
)
from .services import SchoolDomainService
from .in_memory import (
    InMemoryStudentRepository,
    InMemoryParentRepository,
    InMemoryTeacherRepository,
    InMemoryClassRepository,
    InMemoryParentStudentRepository,
    InMemoryTeacherClassRepository,
    InMemoryAttendanceRepository,
)

# Seed in-memory domain repositories
default_students = [
    Student(student_id="student-001", name="Rahul", class_id="10-A"),
    Student(student_id="student-002", name="Ananya", class_id="10-A"),
]

default_parents = [
    Parent(parent_id="parent-001", name="Priya Sharma"),
    Parent(parent_id="parent-002", name="Ananya's Parent"),
    Parent(parent_id="parent-003", name="Rahul and Ananya's Parent"),
]

default_teachers = [
    Teacher(teacher_id="teacher-001", name="Mr. Johnson", subject="Math"),
]

default_classes = [
    Class(class_id="10-A", name="10-A", teacher_id="teacher-001"),
]

default_parent_student = [
    ParentStudent(parent_id="parent-001", student_id="student-001"),
    ParentStudent(parent_id="parent-002", student_id="student-002"),
    ParentStudent(parent_id="parent-003", student_id="student-001"),
    ParentStudent(parent_id="parent-003", student_id="student-002"),
]

default_teacher_class = [
    TeacherClass(teacher_id="teacher-001", class_id="10-A"),
]

default_attendance = [
    AttendanceRecord(
        record_id="att-001",
        student_id="student-001",
        class_id="10-A",
        date=date.today(),
        status=AttendanceStatus.PRESENT,
        recorded_by="teacher-001"
    ),
    AttendanceRecord(
        record_id="att-002",
        student_id="student-002",
        class_id="10-A",
        date=date.today(),
        status=AttendanceStatus.ABSENT,
        recorded_by="teacher-001"
    ),
]

student_repository = InMemoryStudentRepository(default_students)
parent_repository = InMemoryParentRepository(default_parents)
teacher_repository = InMemoryTeacherRepository(default_teachers)
class_repository = InMemoryClassRepository(default_classes)
parent_student_repository = InMemoryParentStudentRepository(default_parent_student)
teacher_class_repository = InMemoryTeacherClassRepository(default_teacher_class)
attendance_repository = InMemoryAttendanceRepository(default_attendance)

# Repository aliases
student_repo = student_repository
parent_repo = parent_repository
teacher_repo = teacher_repository
class_repo = class_repository
parent_student_repo = parent_student_repository
teacher_class_repo = teacher_class_repository
attendance_repo = attendance_repository

school_domain_service = SchoolDomainService(
    student_repo=student_repository,
    parent_repo=parent_repository,
    teacher_repo=teacher_repository,
    class_repo=class_repository,
    parent_student_repo=parent_student_repository,
    teacher_class_repo=teacher_class_repository,
    attendance_repo=attendance_repository,
)
