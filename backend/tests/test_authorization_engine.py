# backend/tests/test_authorization_engine.py
import pytest
from app.authz.engine import AuthorizationEngine
from app.authz.models import AuthorizationDecision
from app.session.models import Identity, Role
from app.domain.seed_data import seed_school_data

# Ensure domain data is seeded
seed_school_data()

engine = AuthorizationEngine()


def test_student_can_view_own_attendance():
    student = Identity(user_id="S001", role=Role.STUDENT, name="Rahul Patel")
    result = engine.authorize_request(student, "view_own_attendance")
    assert result.decision == AuthorizationDecision.ALLOWED
    assert result.allowed is True
    assert result.reason == "AUTHORIZED"


def test_student_cannot_view_all_students():
    student = Identity(user_id="S001", role=Role.STUDENT, name="Rahul Patel")
    result = engine.authorize_request(student, "view_all_students")
    assert result.decision == AuthorizationDecision.DENIED
    assert result.allowed is False
    assert result.reason == "PERMISSION_DENIED"


def test_parent_can_view_linked_child_attendance():
    parent = Identity(user_id="P001", role=Role.PARENT, name="Anita Patel")
    result = engine.authorize_request(
        parent,
        "view_child_attendance",
        {"target_student_id": "S001"}
    )
    assert result.decision == AuthorizationDecision.ALLOWED
    assert result.allowed is True
    assert result.resource_id == "S001"


def test_parent_cannot_view_unlinked_child_attendance():
    parent = Identity(user_id="P001", role=Role.PARENT, name="Anita Patel")
    result = engine.authorize_request(
        parent,
        "view_child_attendance",
        {"target_student_id": "S002"}  # Not P001's child
    )
    assert result.decision == AuthorizationDecision.DENIED
    assert result.allowed is False
    assert result.reason == "RESOURCE_NOT_ALLOWED"


def test_parent_cannot_mark_attendance():
    parent = Identity(user_id="P001", role=Role.PARENT, name="Anita Patel")
    result = engine.authorize_request(
        parent,
        "mark_attendance",
        {"target_student_id": "S001"}
    )
    assert result.decision == AuthorizationDecision.DENIED
    assert result.allowed is False
    assert result.reason == "PERMISSION_DENIED"


def test_teacher_can_view_assigned_class_roster():
    teacher = Identity(user_id="T001", role=Role.TEACHER, name="Kumar Singh")
    result = engine.authorize_request(
        teacher,
        "view_class_roster",
        {"target_class_id": "C001"}
    )
    assert result.decision == AuthorizationDecision.ALLOWED
    assert result.allowed is True


def test_teacher_cannot_access_unassigned_class():
    teacher = Identity(user_id="T001", role=Role.TEACHER, name="Kumar Singh")
    # T001 is assigned to C001, not C002
    result = engine.authorize_request(
        teacher,
        "manage_assignments",
        {"target_class_id": "C002"}
    )
    assert result.decision == AuthorizationDecision.DENIED
    assert result.allowed is False
    assert result.reason == "RESOURCE_NOT_ALLOWED"


def test_teacher_can_mark_attendance_for_student_in_class():
    teacher = Identity(user_id="T001", role=Role.TEACHER, name="Kumar Singh")
    # S001 is in C001 taught by T001
    result = engine.authorize_request(
        teacher,
        "mark_attendance",
        {"target_student_id": "S001"}
    )
    assert result.decision == AuthorizationDecision.ALLOWED
    assert result.allowed is True


def test_principal_can_view_all_students_and_settings():
    principal = Identity(user_id="principal-001", role=Role.PRINCIPAL, name="Dr. Smith")
    result = engine.authorize_request(principal, "view_all_students")
    assert result.decision == AuthorizationDecision.ALLOWED
    assert result.allowed is True

    result_settings = engine.authorize_request(principal, "manage_school_settings")
    assert result_settings.decision == AuthorizationDecision.ALLOWED
    assert result_settings.allowed is True


def test_unknown_intent_returns_denied():
    student = Identity(user_id="S001", role=Role.STUDENT, name="Rahul Patel")
    result = engine.authorize_request(student, "non_existent_intent")
    assert result.decision == AuthorizationDecision.DENIED
    assert result.allowed is False
    assert result.reason == "UNKNOWN_INTENT"
