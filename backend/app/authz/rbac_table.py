"""Single source of truth for role-based intent permissions."""

from app.nlu.intents import Intent
from app.session.models import Role


ROLE_PERMISSIONS: dict[Role, frozenset[Intent]] = {
    Role.STUDENT: frozenset(
        {Intent.VIEW_OWN_ATTENDANCE, Intent.GENERAL_SCHOOL_QUERY}
    ),
    Role.PARENT: frozenset(
        {
            Intent.VIEW_CHILD_ATTENDANCE,
            Intent.GENERAL_SCHOOL_QUERY,
            Intent.ESCALATE_TO_TEACHER,
            Intent.ESCALATE_TO_MANAGEMENT,
        }
    ),
    Role.TEACHER: frozenset(
        {
            Intent.VIEW_CLASS_ATTENDANCE,
            Intent.MARK_ATTENDANCE,
            Intent.GENERAL_SCHOOL_QUERY,
            Intent.ESCALATE_TO_MANAGEMENT,
        }
    ),
    Role.PRINCIPAL: frozenset(
        {
            Intent.VIEW_SCHOOL_ATTENDANCE,
            Intent.VIEW_SCHOOL_ANALYTICS,
            Intent.GENERAL_SCHOOL_QUERY,
            Intent.ESCALATE_TO_MANAGEMENT,
        }
    ),
}
