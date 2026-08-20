"""Tests for Escalation Flow, Escalation Honesty, and Security Audit Logging."""

import pytest
import asyncio
from fastapi.testclient import TestClient

from app.main import app
from app.session.models import Role, Identity
from app.nlu.intents import Intent
from app.nlu.schemas import NLUResult, NLUEntities
from app.routing.dispatcher import ToolDispatcher
from app.mock_api.escalation import escalation_service, EscalationStatus
from app.security.audit_log import audit_logger
from app.domain.seed_data import seed_school_data

client = TestClient(app)
seed_school_data()


@pytest.fixture(autouse=True)
def clean_state():
    escalation_service.clear()
    audit_logger.clear()


@pytest.mark.anyio
async def test_student_can_escalate_to_teacher():
    """Student can escalate to a human teacher."""
    dispatcher = ToolDispatcher()
    student = Identity(user_id="S001", role=Role.STUDENT, name="Rahul Patel", student_id="S001")
    nlu_result = NLUResult(
        intent=Intent.ESCALATE_TO_TEACHER,
        language="en",
        entities=NLUEntities(),
        missing_information=[],
        requires_clarification=False,
        confidence=0.95
    )

    res = await dispatcher.dispatch(student, nlu_result)
    assert res.success is True
    assert res.data is not None
    assert res.data["status"] == EscalationStatus.SUBMITTED.value
    assert res.data["ticket_id"].startswith("ESC-")

    # Verify escalation honesty: ticket actually exists in mock service
    ticket = escalation_service.get_ticket(res.data["ticket_id"])
    assert ticket is not None
    assert ticket.requester_id == "S001"
    assert ticket.target.value == "teacher"

    # Verify audit log
    events = audit_logger.get_events(user_id="S001")
    assert len(events) >= 1
    assert events[0].allowed is True
    assert events[0].intent == "escalate_to_teacher"


@pytest.mark.anyio
async def test_parent_can_escalate_to_management():
    """Parent can escalate to school management."""
    dispatcher = ToolDispatcher()
    parent = Identity(user_id="P001", role=Role.PARENT, name="Anita Patel")
    nlu_result = NLUResult(
        intent=Intent.ESCALATE_TO_MANAGEMENT,
        language="en",
        entities=NLUEntities(),
        missing_information=[],
        requires_clarification=False,
        confidence=0.98
    )

    res = await dispatcher.dispatch(parent, nlu_result)
    assert res.success is True
    assert res.data["target"] == "management"
    assert res.data["ticket_id"].startswith("ESC-")


@pytest.mark.anyio
async def test_student_cannot_escalate_to_management():
    """Student cannot escalate to management directly (RBAC restriction)."""
    dispatcher = ToolDispatcher()
    student = Identity(user_id="S001", role=Role.STUDENT, name="Rahul Patel", student_id="S001")
    nlu_result = NLUResult(
        intent=Intent.ESCALATE_TO_MANAGEMENT,
        language="en",
        entities=NLUEntities(),
        missing_information=[],
        requires_clarification=False,
        confidence=0.95
    )

    res = await dispatcher.dispatch(student, nlu_result)
    assert res.success is False
    assert "permission" in res.message.lower()


def test_escalate_http_endpoint_parent():
    """Test POST /api/v1/escalate via HTTP with authenticated parent cookie."""
    login_res = client.post("/api/v1/auth/login", json={"user_id": "P001"})
    assert login_res.status_code == 200
    cookies = login_res.cookies

    payload = {
        "target": "teacher",
        "reason": "Need to discuss term exam preparation",
        "student_id": "S001"
    }
    response = client.post("/api/v1/escalate", json=payload, cookies=cookies)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["status"] == "submitted"
    assert data["ticket_id"].startswith("ESC-")

    # List tickets
    list_res = client.get("/api/v1/escalate/tickets", cookies=cookies)
    assert list_res.status_code == 200
    list_data = list_res.json()
    assert list_data["count"] >= 1
    assert list_data["tickets"][0]["ticket_id"] == data["ticket_id"]


def test_escalate_http_endpoint_student_forbidden_for_management():
    """Test POST /api/v1/escalate for student requesting management is 403."""
    login_res = client.post("/api/v1/auth/login", json={"user_id": "S001"})
    assert login_res.status_code == 200
    cookies = login_res.cookies

    payload = {
        "target": "management",
        "reason": "General dispute"
    }
    response = client.post("/api/v1/escalate", json=payload, cookies=cookies)
    assert response.status_code == 403
