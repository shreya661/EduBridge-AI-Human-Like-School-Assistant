"""Trusted role-to-tone mapping; persona never grants capabilities."""

from app.session.models import Role


PERSONAS = {
    Role.STUDENT: "Friendly and supportive Academic Assistant",
    Role.PARENT: "Caring, patient and clear Parent Support Assistant",
    Role.TEACHER: "Professional and practical Teaching Assistant",
    Role.PRINCIPAL: "Professional and concise Management Assistant",
}


def persona_for(role: Role) -> str:
    return PERSONAS[role]


def attendance_response(role: Role, result: dict[str, object]) -> str:
    """Use only verified fields. Deterministic templates prevent factual invention."""
    name = str(result["student_name"])
    percentage = result["attendance_percentage"]
    if role == Role.STUDENT:
        return f"You're currently at {percentage}% attendance. Keep an eye on it so you stay on track."
    if role == Role.PARENT:
        return f"{name}'s current attendance is {percentage}%. If you'd like, I can also check recent attendance."
    return f"{name}'s current attendance is {percentage}%."
