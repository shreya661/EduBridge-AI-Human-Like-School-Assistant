"""Tests for SQL (PostgreSQL / SQLite) Database Repositories & Relational Integrity."""

import pytest
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.domain.sql_models import Base
from app.domain.models import Student, Parent, Teacher, Class, ParentStudent, TeacherClass, AttendanceRecord, AttendanceStatus
from app.domain.sql_repositories import (
    SQLStudentRepository,
    SQLParentRepository,
    SQLTeacherRepository,
    SQLClassRepository,
    SQLParentStudentRepository,
    SQLTeacherClassRepository,
    SQLAttendanceRepository,
)
from app.domain.services import SchoolDomainService


@pytest.fixture
def sql_domain_service():
    """Create isolated in-memory SQL database for PostgreSQL schema verification."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    student_repo = SQLStudentRepository(session_factory)
    parent_repo = SQLParentRepository(session_factory)
    teacher_repo = SQLTeacherRepository(session_factory)
    class_repo = SQLClassRepository(session_factory)
    parent_student_repo = SQLParentStudentRepository(session_factory)
    teacher_class_repo = SQLTeacherClassRepository(session_factory)
    attendance_repo = SQLAttendanceRepository(session_factory)

    service = SchoolDomainService(
        student_repo=student_repo,
        parent_repo=parent_repo,
        teacher_repo=teacher_repo,
        class_repo=class_repo,
        parent_student_repo=parent_student_repo,
        teacher_class_repo=teacher_class_repo,
        attendance_repo=attendance_repo,
    )
    return service, student_repo, parent_repo, teacher_repo, class_repo, parent_student_repo, teacher_class_repo, attendance_repo


def test_sql_entities_and_relationships(sql_domain_service):
    """Test SQL tables, foreign relations, and multi-child parent mapping."""
    service, student_repo, parent_repo, teacher_repo, class_repo, parent_student_repo, teacher_class_repo, attendance_repo = sql_domain_service

    # 1. Create Class
    class_repo.create_class(Class(class_id="C001", name="Class 10-A", grade_level=10, section="A"))
    assert class_repo.get_class("C001") is not None

    # 2. Create Students
    student_repo.create_student(Student(student_id="S001", name="Rahul Patel", class_id="C001"))
    student_repo.create_student(Student(student_id="S002", name="Priya Sharma", class_id="C001"))
    student_repo.create_student(Student(student_id="S003", name="Arjun Patel", class_id="C001"))

    # 3. Create Parent and link multiple children
    parent_repo.create_parent(Parent(parent_id="P001", name="Anita Patel", email="anita@example.com", phone="+919876543210"))
    parent_student_repo.create_relationship(ParentStudent(parent_id="P001", student_id="S001"))
    parent_student_repo.create_relationship(ParentStudent(parent_id="P001", student_id="S003"))

    # Verify relational query
    children = service.get_children_for_parent("P001")
    assert len(children) == 2
    child_ids = [c.student_id for c in children]
    assert "S001" in child_ids
    assert "S003" in child_ids
    assert "S002" not in child_ids

    # 4. Create Teacher and assign to class
    teacher_repo.create_teacher(Teacher(teacher_id="T001", name="Kumar Singh", subject="Mathematics"))
    teacher_class_repo.create_relationship(TeacherClass(teacher_id="T001", class_id="C001"))

    classes = service.get_classes_for_teacher("T001")
    assert len(classes) == 1
    assert classes[0].class_id == "C001"

    # 5. Record & Retrieve Attendance
    attendance_repo.create_attendance_record(
        AttendanceRecord(
            record_id="att-sql-001",
            student_id="S001",
            class_id="C001",
            date=date.today(),
            status=AttendanceStatus.PRESENT,
            recorded_by="T001"
        )
    )

    records = service.get_attendance_for_student("S001")
    assert len(records) == 1
    assert records[0].status == AttendanceStatus.PRESENT
    assert records[0].recorded_by == "T001"
