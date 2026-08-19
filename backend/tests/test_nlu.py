"""Tests for validated LLM-backed NLU analysis."""

import json
import unittest
from collections.abc import Mapping
from typing import Any

from app.nlu.llm_client import LLMClient
from app.nlu.intents import Intent


class StaticProvider:
    """Test double that represents a provider's structured response."""

    def __init__(self, response: dict[str, Any]) -> None:
        self._response = response

    async def complete(self, system_prompt: str, user_payload: Mapping[str, Any]) -> str:
        return json.dumps(self._response)


def client_for(response: dict[str, Any]) -> LLMClient:
    return LLMClient(StaticProvider(response), "test prompt")


def result(intent: str, entities: dict[str, str] | None = None, missing: list[str] | None = None) -> dict[str, Any]:
    return {
        "intent": intent,
        "language": "en",
        "entities": entities or {},
        "missing_information": missing or [],
        "confidence": 0.9,
    }


class NLUClientTests(unittest.IsolatedAsyncioTestCase):
    async def test_student_attendance_intent(self) -> None:
        analysis = await client_for(result("view_own_attendance")).analyze_message(
            "What is my attendance?"
        )
        self.assertEqual(analysis.intent, Intent.VIEW_OWN_ATTENDANCE)

    async def test_parent_attendance_intent(self) -> None:
        analysis = await client_for(
            result("view_child_attendance", {"student_name": "Rahul"})
        ).analyze_message("How much attendance does my child Rahul have?")
        self.assertEqual(analysis.intent, Intent.VIEW_CHILD_ATTENDANCE)
        self.assertEqual(analysis.entities.student_name, "Rahul")

    async def test_teacher_attendance_intent(self) -> None:
        analysis = await client_for(
            result("mark_attendance", {"student_name": "Rahul", "date": "today"})
        ).analyze_message("Mark Rahul absent today.")
        self.assertEqual(analysis.intent, Intent.MARK_ATTENDANCE)

    async def test_principal_analytics_intent(self) -> None:
        analysis = await client_for(result("view_school_analytics")).analyze_message(
            "What is the overall attendance?"
        )
        self.assertEqual(analysis.intent, Intent.VIEW_SCHOOL_ANALYTICS)

    async def test_ambiguous_message_does_not_invent_details(self) -> None:
        analysis = await client_for(
            result("unknown", missing=["attendance_subject"])
        ).analyze_message("Attendance?")
        self.assertEqual(analysis.intent, Intent.UNKNOWN)
        self.assertEqual(analysis.entities.student_name, None)
        self.assertIn("attendance_subject", analysis.missing_information)
