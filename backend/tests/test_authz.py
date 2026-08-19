"""Focused RBAC tests using trusted development identities."""

import unittest

from app.authz.guard import AuthorizationReason, is_allowed
from app.nlu.intents import Intent
from app.session.store import development_identity_store


class RBACTests(unittest.TestCase):
    def identity(self, user_id: str):
        identity = development_identity_store.get(user_id)
        assert identity is not None
        return identity

    def test_student_can_view_own_attendance(self) -> None:
        self.assertTrue(is_allowed(self.identity("student-001"), Intent.VIEW_OWN_ATTENDANCE).allowed)

    def test_student_cannot_view_school_analytics(self) -> None:
        result = is_allowed(self.identity("student-001"), Intent.VIEW_SCHOOL_ANALYTICS)
        self.assertEqual(result.reason, AuthorizationReason.ROLE_NOT_PERMITTED)

    def test_parent_can_view_child_attendance(self) -> None:
        self.assertTrue(is_allowed(self.identity("parent-001"), Intent.VIEW_CHILD_ATTENDANCE).allowed)

    def test_parent_cannot_mark_attendance(self) -> None:
        self.assertFalse(is_allowed(self.identity("parent-001"), Intent.MARK_ATTENDANCE).allowed)

    def test_teacher_can_mark_attendance(self) -> None:
        self.assertTrue(is_allowed(self.identity("teacher-001"), Intent.MARK_ATTENDANCE).allowed)

    def test_teacher_can_view_class_attendance(self) -> None:
        self.assertTrue(is_allowed(self.identity("teacher-001"), Intent.VIEW_CLASS_ATTENDANCE).allowed)

    def test_principal_can_view_school_analytics(self) -> None:
        self.assertTrue(is_allowed(self.identity("principal-001"), Intent.VIEW_SCHOOL_ANALYTICS).allowed)

    def test_principal_can_view_school_attendance(self) -> None:
        self.assertTrue(is_allowed(self.identity("principal-001"), Intent.VIEW_SCHOOL_ATTENDANCE).allowed)
