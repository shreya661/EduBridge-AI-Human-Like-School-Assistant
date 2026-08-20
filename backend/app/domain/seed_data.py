# backend/app/domain/seed_data.py
from datetime import date, datetime
from . import (
    student_repo, parent_repo, teacher_repo, class_repo,
    parent_student_repo, teacher_class_repo, school_domain_service,
    attendance_repo
)
from .models import Student, Parent, Teacher, Class, ParentStudent, TeacherClass


def seed_school_data():
    """Seed the school domain with fictional development data"""
    
    # Create students
    student_001 = Student(
        student_id="S001",
        name="Rahul Patel",
        email="rahul.patel@example.com",
        class_id="C001"
    )
    student_002 = Student(
        student_id="S002",
        name="Ananya Sharma",
        email="ananya.sharma@example.com",
        class_id="C002"
    )
    student_003 = Student(
        student_id="S003",
        name="Arjun Kumar",
        email="arjun.kumar@example.com",
        class_id="C001"
    )
    
    student_repo.create_student(student_001)
    student_repo.create_student(student_002)
    student_repo.create_student(student_003)
    
    # Create parents
    parent_001 = Parent(
        parent_id="P001",
        name="Anita Patel",
        email="anita.patel@example.com",
        phone="+1234567890"
    )
    parent_002 = Parent(
        parent_id="P002",
        name="Rajesh Sharma",
        email="rajesh.sharma@example.com",
        phone="+1234567891"
    )
    
    parent_repo.create_parent(parent_001)
    parent_repo.create_parent(parent_002)
    
    # Create teachers
    teacher_001 = Teacher(
        teacher_id="T001",
        name="Kumar Singh",
        email="kumar.singh@example.com",
        subject="Mathematics"
    )
    teacher_002 = Teacher(
        teacher_id="T002",
        name="Priya Nair",
        email="priya.nair@example.com",
        subject="Science"
    )
    
    teacher_repo.create_teacher(teacher_001)
    teacher_repo.create_teacher(teacher_002)
    
    # Create classes
    class_001 = Class(
        class_id="C001",
        name="10-A",
        grade_level=10,
        section="A",
        academic_year="2026-2027",
        teacher_id="T001"
    )
    class_002 = Class(
        class_id="C002",
        name="10-B",
        grade_level=10,
        section="B",
        academic_year="2026-2027",
        teacher_id="T002"
    )
    
    class_repo.create_class(class_001)
    class_repo.create_class(class_002)
    
    # Create parent-student relationships
    parent_student_001 = ParentStudent(
        parent_id="P001",
        student_id="S001"
    )
    parent_student_002 = ParentStudent(
        parent_id="P001",
        student_id="S003"
    )
    parent_student_003 = ParentStudent(
        parent_id="P002",
        student_id="S002"
    )
    
    parent_student_repo.create_relationship(parent_student_001)
    parent_student_repo.create_relationship(parent_student_002)
    parent_student_repo.create_relationship(parent_student_003)
    
    # Create teacher-class relationships
    teacher_class_001 = TeacherClass(
        teacher_id="T001",
        class_id="C001"
    )
    teacher_class_002 = TeacherClass(
        teacher_id="T002",
        class_id="C002"
    )
    
    teacher_class_repo.create_relationship(teacher_class_001)
    teacher_class_repo.create_relationship(teacher_class_002)
    
    # Create some initial attendance records
    from uuid import uuid4
    from .models import AttendanceRecord, AttendanceStatus
    
    attendance_repo.create_attendance_record(AttendanceRecord(
        record_id=f"att-{uuid4().hex[:8]}",
        student_id="S001",
        class_id="C001",
        date=date.today(),
        status=AttendanceStatus.PRESENT,
        recorded_by="T001"
    ))
    
    attendance_repo.create_attendance_record(AttendanceRecord(
        record_id=f"att-{uuid4().hex[:8]}",
        student_id="S002",
        class_id="C002",
        date=date.today(),
        status=AttendanceStatus.ABSENT,
        recorded_by="T002"
    ))
    
    print("School domain data seeded successfully!")


# Run seeding
seed_school_data()
