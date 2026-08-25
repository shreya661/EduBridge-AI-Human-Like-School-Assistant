# backend/app/authz/rbac_table.py
from typing import Dict, List, Set
from app.session.models import Role
from app.nlu.intents import Intent

# Define permissions table
PERMISSIONS_TABLE: Dict[Role, Set[str]] = {
    Role.STUDENT: {
        "view_own_profile",
        "view_own_grades",
        "view_own_attendance",
        "submit_assignment",
        "general_school_query",
        "escalate_to_teacher",
    },
    Role.PARENT: {
        "view_child_profile",
        "view_child_grades", 
        "view_child_attendance",
        "communicate_with_teachers",
        "general_school_query",
        "escalate_to_teacher",
        "escalate_to_management",
    },
    Role.TEACHER: {
        "view_class_roster",
        "view_student_profiles",
        "view_student_grades",
        "view_student_attendance",
        "view_class_attendance",
        "mark_attendance",
        "manage_assignments",
        "grade_submissions",
        "general_school_query",
        "escalate_to_management",
    },
    Role.PRINCIPAL: {
        "view_all_students",
        "view_all_teachers", 
        "view_all_classes",
        "manage_school_settings",
        "generate_reports",
        "view_all_attendance",
        "view_school_attendance",
        "view_school_analytics",
        "manage_users",
        "general_school_query",
        "escalate_to_management",
    }
}

ROLE_PERMISSIONS: Dict[Role, frozenset] = {
    Role.STUDENT: frozenset(
        {
            Intent.VIEW_OWN_ATTENDANCE,
            Intent.GENERAL_SCHOOL_QUERY,
            Intent.ESCALATE_TO_TEACHER,
            "view_own_attendance",
            "view_own_profile",
            "general_school_query",
            "escalate_to_teacher",
        }
    ),
    Role.PARENT: frozenset(
        {
            Intent.VIEW_CHILD_ATTENDANCE,
            Intent.GENERAL_SCHOOL_QUERY,
            Intent.ESCALATE_TO_TEACHER,
            Intent.ESCALATE_TO_MANAGEMENT,
            "view_child_attendance",
            "view_child_profile",
        }
    ),
    Role.TEACHER: frozenset(
        {
            Intent.VIEW_CLASS_ATTENDANCE,
            Intent.MARK_ATTENDANCE,
            Intent.GENERAL_SCHOOL_QUERY,
            Intent.ESCALATE_TO_MANAGEMENT,
            "view_class_attendance",
            "mark_attendance",
        }
    ),
    Role.PRINCIPAL: frozenset(
        {
            Intent.VIEW_SCHOOL_ATTENDANCE,
            Intent.VIEW_SCHOOL_ANALYTICS,
            Intent.GENERAL_SCHOOL_QUERY,
            Intent.ESCALATE_TO_MANAGEMENT,
            "view_all_students",
            "view_school_attendance",
            "view_all_attendance",
            "view_school_analytics",
        }
    ),
}


def has_permission(role: Role, action: str) -> bool:
    """Check if role has permission for action"""
    return action in PERMISSIONS_TABLE.get(role, set())
