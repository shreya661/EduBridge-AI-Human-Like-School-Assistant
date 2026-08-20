# backend/app/session/store.py - Updated to use domain service for relationships
from typing import Dict, Optional
from .models import Identity, Role
from ..domain import school_domain_service


class InMemoryIdentityStore:
    def __init__(self):
        self.identities: Dict[str, Identity] = {
            "student-001": Identity(
                user_id="student-001",
                role=Role.STUDENT,
                name="Rahul",
                student_id="student-001",
            ),
            "student-002": Identity(
                user_id="student-002",
                role=Role.STUDENT,
                name="Ananya",
                student_id="student-002",
            ),
            "parent-001": Identity(
                user_id="parent-001",
                role=Role.PARENT,
                name="Priya Sharma",
            ),
            "parent-002": Identity(
                user_id="parent-002",
                role=Role.PARENT,
                name="Ananya's Parent",
            ),
            "parent-003": Identity(
                user_id="parent-003",
                role=Role.PARENT,
                name="Rahul and Ananya's Parent",
            ),
            "teacher-001": Identity(
                user_id="teacher-001",
                role=Role.TEACHER,
                name="Mr. Johnson",
            ),
            "principal-001": Identity(
                user_id="principal-001",
                role=Role.PRINCIPAL,
                name="Dr. Smith",
            ),
            "S001": Identity(
                user_id="S001",
                role=Role.STUDENT,
                name="Rahul Patel",
                student_id="S001",
            ),
            "S002": Identity(
                user_id="S002",
                role=Role.STUDENT,
                name="Ananya Sharma",
                student_id="S002",
            ),
            "S003": Identity(
                user_id="S003",
                role=Role.STUDENT,
                name="Arjun Kumar",
                student_id="S003",
            ),
            "P001": Identity(
                user_id="P001",
                role=Role.PARENT,
                name="Anita Patel",
            ),
            "P002": Identity(
                user_id="P002",
                role=Role.PARENT,
                name="Rajesh Sharma",
            ),
            "T001": Identity(
                user_id="T001",
                role=Role.TEACHER,
                name="Kumar Singh",
            ),
        }

    def get(self, user_id: str) -> Optional[Identity]:
        return self.identities.get(user_id)

    def get_identity(self, user_id: str) -> Optional[Identity]:
        return self.identities.get(user_id)

    def get_all_identities(self) -> Dict[str, Identity]:
        return self.identities.copy()


# Global instance for development
identity_store = InMemoryIdentityStore()
development_identity_store = identity_store
