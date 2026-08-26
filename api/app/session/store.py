# backend/app/session/store.py - Updated with database lookup and role-aware identity store
from typing import Dict, Optional
from .models import Identity, Role
from ..domain import school_domain_service
from ..domain.database import SessionLocal
from ..domain.sql_models import SQLUser


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
            # Default seeded 10-char Alphanumeric Accounts
            "STU10A88F2": Identity(
                user_id="STU10A88F2",
                role=Role.STUDENT,
                name="Aarav Patel",
                student_id="STU10A88F2",
            ),
            "TCH90K11X4": Identity(
                user_id="TCH90K11X4",
                role=Role.TEACHER,
                name="Kumar Singh",
            ),
            "PAR81L90V7": Identity(
                user_id="PAR81L90V7",
                role=Role.PARENT,
                name="Anita Patel",
            ),
            "PRN10A99X1": Identity(
                user_id="PRN10A99X1",
                role=Role.PRINCIPAL,
                name="Dr. Smith",
            ),
            # Legacy short IDs for backward test compatibility
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
        return self.get_identity(user_id)

    def get_identity(self, user_id: str) -> Optional[Identity]:
        if not user_id:
            return None
        
        # 1. Fast in-memory cache check
        if user_id in self.identities:
            return self.identities[user_id]
        
        # 2. Database lookup in SQLUser
        if SessionLocal:
            try:
                with SessionLocal() as session:
                    user = session.query(SQLUser).filter(
                        (SQLUser.user_id == user_id) | (SQLUser.email == user_id)
                    ).first()
                    if user:
                        try:
                            role_enum = Role(user.role.upper())
                        except ValueError:
                            role_enum = Role.STUDENT
                        
                        identity = Identity(
                            user_id=user.user_id,
                            role=role_enum,
                            name=user.name,
                            student_id=user.user_id if role_enum == Role.STUDENT else None,
                        )
                        self.identities[user.user_id] = identity
                        return identity
            except Exception:
                pass

        return None

    def add_identity(self, identity: Identity):
        self.identities[identity.user_id] = identity

    def get_all_identities(self) -> Dict[str, Identity]:
        return self.identities.copy()


# Global instance for development
identity_store = InMemoryIdentityStore()
development_identity_store = identity_store
