"""Script to initialize and seed PostgreSQL database with test records."""

import os
import sys
from datetime import date, timedelta
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(backend_dir))

from app.domain.database import SessionLocal, engine
from app.domain.sql_models import (
    Base, SQLStudent, SQLParent, SQLTeacher, SQLClass,
    SQLParentStudent, SQLTeacherClass, SQLAttendanceRecord
)


def seed_database():
    if engine is None or SessionLocal is None:
        print("[-] DATABASE_URL is not configured in .env. Please set it before running this script.")
        print("    Example: DATABASE_URL=postgresql://postgres:postgres@localhost:5432/school_erp")
        return

    print(f"[+] Connecting to PostgreSQL via {engine.url}...")
    Base.metadata.create_all(bind=engine)
    print("[+] Created all relational tables.")

    with SessionLocal() as session:
        # Check if classes already exist
        if session.query(SQLClass).first():
            print("[*] Database already populated with seed data. Skipping insert.")
            return

        print("[+] Seeding default classes...")
        classes = [
            SQLClass(class_id="C001", name="Class 10-A", grade_level=10, section="A", teacher_id="T001"),
            SQLClass(class_id="C002", name="Class 10-B", grade_level=10, section="B", teacher_id="T002"),
            SQLClass(class_id="C003", name="Class 9-A", grade_level=9, section="A", teacher_id="T001"),
            SQLClass(class_id="C004", name="Class 9-B", grade_level=9, section="B", teacher_id="T002"),
        ]
        session.add_all(classes)

        print("[+] Seeding default students...")
        students = [
            SQLStudent(student_id="S001", name="Rahul Patel", class_id="C001"),
            SQLStudent(student_id="S002", name="Priya Sharma", class_id="C001"),
            SQLStudent(student_id="S003", name="Arjun Patel", class_id="C002"),
            SQLStudent(student_id="S004", name="Aarav Gupta", class_id="C001"),
            SQLStudent(student_id="S005", name="Diya Mehta", class_id="C002"),
        ]
        session.add_all(students)

        print("[+] Seeding default parents...")
        parents = [
            SQLParent(parent_id="P001", name="Anita Patel", email="anita.patel@example.com", phone="+919876543210"),
            SQLParent(parent_id="P002", name="Rajesh Sharma", email="rajesh.sharma@example.com", phone="+919876543211"),
        ]
        session.add_all(parents)
        session.flush()

        print("[+] Seeding parent-student relationships...")
        parent_students = [
            SQLParentStudent(parent_id="P001", student_id="S001"),
            SQLParentStudent(parent_id="P001", student_id="S003"),
            SQLParentStudent(parent_id="P002", student_id="S002"),
        ]
        session.add_all(parent_students)

        print("[+] Seeding teachers...")
        teachers = [
            SQLTeacher(teacher_id="T001", name="Kumar Singh", subject="Mathematics"),
            SQLTeacher(teacher_id="T002", name="Sunita Verma", subject="Science"),
        ]
        session.add_all(teachers)
        session.flush()

        print("[+] Seeding teacher-class assignments...")
        teacher_classes = [
            SQLTeacherClass(teacher_id="T001", class_id="C001"),
            SQLTeacherClass(teacher_id="T001", class_id="C003"),
            SQLTeacherClass(teacher_id="T002", class_id="C002"),
            SQLTeacherClass(teacher_id="T002", class_id="C004"),
        ]
        session.add_all(teacher_classes)

        print("[+] Seeding attendance records...")
        today = date.today()
        records = []
        for i in range(14):
            d = today - timedelta(days=i)
            records.append(SQLAttendanceRecord(record_id=f"att-s001-{i}", student_id="S001", class_id="C001", date=d, status="PRESENT", recorded_by="T001"))
            records.append(SQLAttendanceRecord(record_id=f"att-s002-{i}", student_id="S002", class_id="C001", date=d, status="PRESENT" if i % 4 != 0 else "ABSENT", recorded_by="T001"))
            records.append(SQLAttendanceRecord(record_id=f"att-s003-{i}", student_id="S003", class_id="C002", date=d, status="PRESENT" if i % 5 != 0 else "LATE", recorded_by="T002"))
        
        session.add_all(records)
        session.commit()
        print("[+] PostgreSQL database successfully seeded with students, classes, and attendance records!")


if __name__ == "__main__":
    seed_database()
