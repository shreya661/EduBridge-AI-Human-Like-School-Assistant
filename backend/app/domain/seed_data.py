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

    # ── 1. Create classes FIRST (students FK → classes) ──────────────────────
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

    # ── 2. Legacy class for unit tests ────────────────────────────────────────
    teacher_legacy_1 = Teacher(teacher_id="teacher-001", name="Mr. Johnson", subject="Mathematics")
    teacher_repo.create_teacher(teacher_legacy_1)

    class_legacy_1 = Class(class_id="10-A", name="10-A", teacher_id="teacher-001")
    class_repo.create_class(class_legacy_1)

    # ── 3. Create students (after classes exist) ──────────────────────────────
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

    # Legacy students
    student_legacy_1 = Student(student_id="student-001", name="Rahul", class_id="10-A")
    student_legacy_2 = Student(student_id="student-002", name="Ananya", class_id="10-A")
    student_repo.create_student(student_legacy_1)
    student_repo.create_student(student_legacy_2)

    # ── 4. Create parents ─────────────────────────────────────────────────────
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

    # Legacy parents
    parent_legacy_1 = Parent(parent_id="parent-001", name="Priya Sharma")
    parent_legacy_2 = Parent(parent_id="parent-002", name="Ananya's Parent")
    parent_legacy_3 = Parent(parent_id="parent-003", name="Rahul and Ananya's Parent")
    parent_repo.create_parent(parent_legacy_1)
    parent_repo.create_parent(parent_legacy_2)
    parent_repo.create_parent(parent_legacy_3)

    # ── 5. Create teachers ────────────────────────────────────────────────────
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

    # ── 6. Parent-student relationships ──────────────────────────────────────
    parent_student_repo.create_relationship(ParentStudent(parent_id="P001", student_id="S001"))
    parent_student_repo.create_relationship(ParentStudent(parent_id="P001", student_id="S003"))
    parent_student_repo.create_relationship(ParentStudent(parent_id="P002", student_id="S002"))
    parent_student_repo.create_relationship(ParentStudent(parent_id="parent-001", student_id="student-001"))
    parent_student_repo.create_relationship(ParentStudent(parent_id="parent-002", student_id="student-002"))
    parent_student_repo.create_relationship(ParentStudent(parent_id="parent-003", student_id="student-001"))
    parent_student_repo.create_relationship(ParentStudent(parent_id="parent-003", student_id="student-002"))

    # ── 7. Teacher-class relationships ────────────────────────────────────────
    teacher_class_repo.create_relationship(TeacherClass(teacher_id="T001", class_id="C001"))
    teacher_class_repo.create_relationship(TeacherClass(teacher_id="T002", class_id="C002"))
    teacher_class_repo.create_relationship(TeacherClass(teacher_id="teacher-001", class_id="10-A"))

    # ── 8. Attendance records ─────────────────────────────────────────────────
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

    # ── 9. 10-character alphanumeric accounts ─────────────────────────────────
    student_10 = Student(student_id="STU10A88F2", name="Aarav Patel", email="aarav.student@school.edu", class_id="C001")
    student_repo.create_student(student_10)

    teacher_10 = Teacher(teacher_id="TCH90K11X4", name="Kumar Singh", email="kumar.teacher@school.edu", subject="Mathematics")
    teacher_repo.create_teacher(teacher_10)
    teacher_class_repo.create_relationship(TeacherClass(teacher_id="TCH90K11X4", class_id="C001"))

    parent_10 = Parent(parent_id="PAR81L90V7", name="Anita Patel", email="anita.parent@school.edu", phone="+91 98765 43210")
    parent_repo.create_parent(parent_10)
    parent_student_repo.create_relationship(ParentStudent(parent_id="PAR81L90V7", student_id="STU10A88F2"))

    # ── 10. Seed SQL user credentials ─────────────────────────────────────────
    try:
        from ..auth.security import hash_password
        from ..domain.database import SessionLocal
        from ..domain.sql_models import SQLUser

        if SessionLocal:
            with SessionLocal() as session:
                pw_hash, salt = hash_password("Password@123")
                users_to_seed = [
                    SQLUser(user_id="STU10A88F2", name="Aarav Patel", email="aarav.student@school.edu", role="STUDENT", password_hash=pw_hash, salt=salt),
                    SQLUser(user_id="TCH90K11X4", name="Kumar Singh", email="kumar.teacher@school.edu", role="TEACHER", password_hash=pw_hash, salt=salt),
                    SQLUser(user_id="PAR81L90V7", name="Anita Patel", email="anita.parent@school.edu", role="PARENT", password_hash=pw_hash, salt=salt),
                    SQLUser(user_id="PRN10A99X1", name="Dr. Smith", email="principal@school.edu", role="PRINCIPAL", password_hash=pw_hash, salt=salt),
                    SQLUser(user_id="S001", name="Rahul Patel", email="rahul.patel@example.com", role="STUDENT", password_hash=pw_hash, salt=salt),
                    SQLUser(user_id="T001", name="Kumar Singh", email="kumar.singh@example.com", role="TEACHER", password_hash=pw_hash, salt=salt),
                    SQLUser(user_id="P001", name="Anita Patel", email="anita.patel@example.com", role="PARENT", password_hash=pw_hash, salt=salt),
                    SQLUser(user_id="principal-001", name="Dr. Smith", email="principal001@example.com", role="PRINCIPAL", password_hash=pw_hash, salt=salt),
                ]
                for u in users_to_seed:
                    session.merge(u)
                session.commit()
    except Exception:
        pass

    print("School domain data seeded successfully!")


# NOTE: Do NOT call seed_school_data() here at module level.
# It is called from app.main startup_event() instead.
