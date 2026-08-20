"""Controlled intent vocabulary for the school assistant."""

from enum import StrEnum


class Intent(StrEnum):
    VIEW_OWN_ATTENDANCE = "view_own_attendance"
    VIEW_CHILD_ATTENDANCE = "view_child_attendance"
    MARK_ATTENDANCE = "mark_attendance"
    VIEW_CLASS_ATTENDANCE = "view_class_attendance"
    VIEW_SCHOOL_ATTENDANCE = "view_school_attendance"
    VIEW_SCHOOL_ANALYTICS = "view_school_analytics"
    GREETING = "greeting"
    CLARIFICATION_NEEDED = "clarification_needed"
    UNSUPPORTED_REQUEST = "unsupported_request"
    ESCALATE_TO_TEACHER = "escalate_to_teacher"
    ESCALATE_TO_MANAGEMENT = "escalate_to_management"
    GENERAL_SCHOOL_QUERY = "general_school_query"
    UNKNOWN = "unknown"
