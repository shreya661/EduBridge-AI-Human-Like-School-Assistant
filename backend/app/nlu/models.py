"""Typed data models and entity structures for NLU layer."""

from typing import Optional
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field

from app.nlu.intents import Intent
from app.nlu.schemas import NLUEntities, NLUResult


class IntentType(str, Enum):
    # Student intents
    VIEW_OWN_ATTENDANCE = "view_own_attendance"
    VIEW_OWN_PROFILE = "view_own_profile"
    SUBMIT_ASSIGNMENT = "submit_assignment"
    
    # Parent intents
    VIEW_CHILD_ATTENDANCE = "view_child_attendance"
    VIEW_CHILD_PROFILE = "view_child_profile"
    VIEW_CHILD_GRADES = "view_child_grades"
    COMMUNICATE_WITH_TEACHERS = "communicate_with_teachers"
    
    # Teacher intents
    VIEW_CLASS_ROSTER = "view_class_roster"
    VIEW_STUDENT_ATTENDANCE = "view_student_attendance"
    VIEW_STUDENT_PROFILE = "view_student_profile"
    VIEW_STUDENT_GRADES = "view_student_grades"
    MARK_ATTENDANCE = "mark_attendance"
    MANAGE_ASSIGNMENTS = "manage_assignments"
    GRADE_SUBMISSIONS = "grade_submissions"
    
    # Principal intents
    VIEW_ALL_STUDENTS = "view_all_students"
    VIEW_ALL_TEACHERS = "view_all_teachers"
    VIEW_ALL_CLASSES = "view_all_classes"
    MANAGE_SCHOOL_SETTINGS = "manage_school_settings"
    GENERATE_REPORTS = "generate_reports"
    VIEW_ALL_ATTENDANCE = "view_all_attendance"
    MANAGE_USERS = "manage_users"
    
    # General intents
    GREETING = "greeting"
    CLARIFICATION_NEEDED = "clarification_needed"
    UNSUPPORTED_REQUEST = "unsupported_request"


class Entity(BaseModel):
    model_config = ConfigDict(extra="forbid")

    student_name: Optional[str] = None
    student_id: Optional[str] = None
    class_name: Optional[str] = None
    class_id: Optional[str] = None
    date_expression: Optional[str] = None
    attendance_status: Optional[str] = None
    target_user: Optional[str] = None


__all__ = [
    "IntentType",
    "Intent",
    "Entity",
    "NLUEntities",
    "NLUResult",
]
