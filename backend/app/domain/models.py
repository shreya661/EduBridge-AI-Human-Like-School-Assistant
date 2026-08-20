# backend/app/domain/models.py
from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional, List
from enum import Enum


class UserRole(str, Enum):
    STUDENT = "STUDENT"
    PARENT = "PARENT"
    TEACHER = "TEACHER"
    PRINCIPAL = "PRINCIPAL"


class Student(BaseModel):
    student_id: str
    name: str
    email: Optional[str] = None
    class_id: Optional[str] = None
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class Parent(BaseModel):
    parent_id: str
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class Teacher(BaseModel):
    teacher_id: str
    name: str
    email: Optional[str] = None
    subject: Optional[str] = None
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class Class(BaseModel):
    class_id: str
    name: str  # e.g., "10-A", "Grade 10 Math"
    grade_level: Optional[int] = None
    section: Optional[str] = None
    academic_year: Optional[str] = None
    teacher_id: Optional[str] = None
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class ParentStudent(BaseModel):
    """Relationship between parent and student"""
    parent_id: str
    student_id: str
    relationship_type: str = "guardian"  # guardian, parent, etc.
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)


class TeacherClass(BaseModel):
    """Relationship between teacher and class"""
    teacher_id: str
    class_id: str
    assigned_date: date = Field(default_factory=date.today)
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)


class AttendanceStatus(str, Enum):
    PRESENT = "PRESENT"
    ABSENT = "ABSENT"
    LATE = "LATE"
    EXCUSED = "EXCUSED"


class AttendanceRecord(BaseModel):
    record_id: str
    student_id: str
    class_id: Optional[str] = None
    date: date
    status: AttendanceStatus
    recorded_by: str  # user_id of who recorded it
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
