"""Ownership validation tests kept separate from RBAC tests."""

import unittest

from app.authz.guard import AuthorizationReason
from app.authz.ownership import validate_ownership
from app.nlu.intents import Intent
from app.session.store import development_identity_store


class OwnershipTests(unittest.TestCase):
    def identity(self, user_id: str):
        identity = development_identity_store.get(user_id)
        assert identity is not None
        return identity

    def test_student_cannot_access_another_students_attendance(self) -> None:
        result = validate_ownership(
            self.identity("student-001"), Intent.VIEW_OWN_ATTENDANCE, student_id="student-002"
        )
        self.assertEqual(result.reason, AuthorizationReason.OWNERSHIP_CHECK_FAILED)

    def test_parent_can_access_own_child(self) -> None:
        result = validate_ownership(
            self.identity("parent-001"), Intent.VIEW_CHILD_ATTENDANCE, student_id="student-001"
        )
        self.assertTrue(result.allowed)

    def test_parent_cannot_access_another_parents_child(self) -> None:
        result = validate_ownership(
            self.identity("parent-001"), Intent.VIEW_CHILD_ATTENDANCE, student_id="student-002"
        )
        self.assertFalse(result.allowed)

    def test_teacher_cannot_access_unrelated_class(self) -> None:
        result = validate_ownership(
            self.identity("teacher-001"), Intent.VIEW_CLASS_ATTENDANCE, class_name="11-B"
        )
        self.assertFalse(result.allowed)
