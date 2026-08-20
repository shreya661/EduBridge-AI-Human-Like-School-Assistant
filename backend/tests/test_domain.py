# backend/tests/test_domain.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.domain import school_domain_service, student_repo, parent_repo, teacher_repo, class_repo
from app.domain.seed_data import seed_school_data

client = TestClient(app)
seed_school_data()


def test_student_creation_and_retrieval():
    """Test student domain operations"""
    student = school_domain_service.student_repo.get_student("S001")
    assert student is not None
    assert student.name == "Rahul Patel"
    assert student.class_id == "C001"


def test_parent_creation_and_retrieval():
    """Test parent domain operations"""
    parent = school_domain_service.parent_repo.get_parent("P001")
    assert parent is not None
    assert parent.name == "Anita Patel"


def test_teacher_creation_and_retrieval():
    """Test teacher domain operations"""
    teacher = school_domain_service.teacher_repo.get_teacher("T001")
    assert teacher is not None
    assert teacher.name == "Kumar Singh"


def test_class_creation_and_retrieval():
    """Test class domain operations"""
    class_ = school_domain_service.class_repo.get_class("C001")
    assert class_ is not None
    assert class_.name == "10-A"


def test_parent_student_relationship():
    """Test parent-student relationship"""
    children = school_domain_service.get_children_for_parent("P001")
    assert len(children) == 2
    child_ids = [c.student_id for c in children]
    assert "S001" in child_ids
    assert "S003" in child_ids


def test_teacher_class_relationship():
    """Test teacher-class relationship"""
    classes = school_domain_service.get_classes_for_teacher("T001")
    assert len(classes) == 1
    assert classes[0].class_id == "C001"


def test_student_class_enrollment():
    """Test student-class relationship"""
    students = school_domain_service.get_students_in_class("C001")
    assert len(students) == 2
    student_ids = [s.student_id for s in students]
    assert "S001" in student_ids
    assert "S003" in student_ids


def test_attendance_recording():
    """Test attendance domain operations"""
    from datetime import date
    from app.domain.models import AttendanceStatus
    
    # Record attendance
    record = school_domain_service.record_attendance(
        student_id="S001",
        class_id="C001",
        date=date.today(),
        status=AttendanceStatus.LATE,
        recorded_by="T001"
    )
    
    assert record.student_id == "S001"
    assert record.class_id == "C001"
    assert record.status == AttendanceStatus.LATE


def test_attendance_retrieval():
    """Test attendance retrieval"""
    records = school_domain_service.get_attendance_for_student("S001")
    assert len(records) >= 1
    assert records[0].student_id == "S001"
