"""SQLAlchemy ORM Models for PostgreSQL / SQLite Database Persistence."""

from datetime import date, datetime, timezone
from sqlalchemy import Column, String, Integer, Date, DateTime, ForeignKey, Table, Enum as SQLEnum
from sqlalchemy.orm import declarative_base, relationship
import enum

Base = declarative_base()


class SQLAttendanceStatus(str, enum.Enum):
    PRESENT = "PRESENT"
    ABSENT = "ABSENT"
    LATE = "LATE"
    EXCUSED = "EXCUSED"


class SQLClass(Base):
    __tablename__ = "classes"

    class_id = Column(String(50), primary_key=True)
    name = Column(String(100), nullable=False)
    grade_level = Column(Integer, nullable=True)
    section = Column(String(10), nullable=True)
    teacher_id = Column(String(50), nullable=True)

    students = relationship("SQLStudent", back_populates="school_class")
    teachers = relationship("SQLTeacherClass", back_populates="school_class")


class SQLStudent(Base):
    __tablename__ = "students"

    student_id = Column(String(50), primary_key=True)
    name = Column(String(150), nullable=False)
    class_id = Column(String(50), ForeignKey("classes.class_id"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    school_class = relationship("SQLClass", back_populates="students")
    parents = relationship("SQLParentStudent", back_populates="student")
    attendance_records = relationship("SQLAttendanceRecord", back_populates="student")


class SQLParent(Base):
    __tablename__ = "parents"

    parent_id = Column(String(50), primary_key=True)
    name = Column(String(150), nullable=False)
    email = Column(String(150), nullable=True)
    phone = Column(String(50), nullable=True)

    children = relationship("SQLParentStudent", back_populates="parent")


class SQLTeacher(Base):
    __tablename__ = "teachers"

    teacher_id = Column(String(50), primary_key=True)
    name = Column(String(150), nullable=False)
    subject = Column(String(100), nullable=True)

    classes = relationship("SQLTeacherClass", back_populates="teacher")


class SQLParentStudent(Base):
    __tablename__ = "parent_students"

    id = Column(Integer, primary_key=True, autoincrement=True)
    parent_id = Column(String(50), ForeignKey("parents.parent_id"), nullable=False)
    student_id = Column(String(50), ForeignKey("students.student_id"), nullable=False)

    parent = relationship("SQLParent", back_populates="children")
    student = relationship("SQLStudent", back_populates="parents")


class SQLTeacherClass(Base):
    __tablename__ = "teacher_classes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    teacher_id = Column(String(50), ForeignKey("teachers.teacher_id"), nullable=False)
    class_id = Column(String(50), ForeignKey("classes.class_id"), nullable=False)

    teacher = relationship("SQLTeacher", back_populates="classes")
    school_class = relationship("SQLClass", back_populates="teachers")


class SQLAttendanceRecord(Base):
    __tablename__ = "attendance_records"

    record_id = Column(String(60), primary_key=True)
    student_id = Column(String(50), ForeignKey("students.student_id"), nullable=False)
    class_id = Column(String(50), nullable=True)
    date = Column(Date, nullable=False)
    status = Column(String(20), nullable=False, default="PRESENT")
    recorded_by = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    student = relationship("SQLStudent", back_populates="attendance_records")


class SQLUser(Base):
    __tablename__ = "users"

    user_id = Column(String(50), primary_key=True)
    name = Column(String(150), nullable=False)
    email = Column(String(150), nullable=True)
    role = Column(String(50), nullable=False)
    password_hash = Column(String(255), nullable=False)
    salt = Column(String(64), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
