"""Development-only identity store; replace with real authentication in a later phase."""

from app.session.models import Identity, Role


class DevelopmentIdentityStore:
    """Controlled, in-memory identities for local authorization development."""

    def __init__(self, identities: tuple[Identity, ...]) -> None:
        self._identities = {identity.user_id: identity for identity in identities}

    def get(self, user_id: str) -> Identity | None:
        """Look up an identity supplied by the application session, not request role data."""
        return self._identities.get(user_id)


DEVELOPMENT_IDENTITIES = (
    Identity(
        user_id="student-001",
        role=Role.STUDENT,
        name="Rahul",
        student_id="student-001",
    ),
    Identity(
        user_id="student-002",
        role=Role.STUDENT,
        name="Ananya",
        student_id="student-002",
    ),
    Identity(
        user_id="parent-001",
        role=Role.PARENT,
        name="Rahul's Parent",
        associated_student_ids=("student-001",),
    ),
    Identity(
        user_id="parent-002",
        role=Role.PARENT,
        name="Ananya's Parent",
        associated_student_ids=("student-002",),
    ),
    Identity(
        user_id="parent-003",
        role=Role.PARENT,
        name="Rahul and Ananya's Parent",
        associated_student_ids=("student-001", "student-002"),
    ),
    Identity(
        user_id="teacher-001",
        role=Role.TEACHER,
        name="Class Teacher",
        assigned_class_names=("10-A",),
    ),
    Identity(
        user_id="principal-001",
        role=Role.PRINCIPAL,
        name="Principal",
    ),
)


development_identity_store = DevelopmentIdentityStore(DEVELOPMENT_IDENTITIES)
