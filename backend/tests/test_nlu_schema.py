"""Schema validation tests for the NLU boundary."""

import unittest

from pydantic import ValidationError

from app.nlu.intents import Intent
from app.nlu.schemas import NLUResult


class NLUResultSchemaTests(unittest.TestCase):
    def test_valid_nlu_result_is_accepted(self) -> None:
        result = NLUResult.model_validate(
            {
                "intent": "view_own_attendance",
                "language": "en",
                "entities": {},
                "missing_information": [],
                "confidence": 0.96,
            }
        )
        self.assertEqual(result.intent, Intent.VIEW_OWN_ATTENDANCE)

    def test_invalid_intent_is_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            NLUResult.model_validate(
                {
                    "intent": "grant_attendance_access",
                    "language": "en",
                    "entities": {},
                    "missing_information": [],
                    "confidence": 0.5,
                }
            )

    def test_missing_information_is_preserved(self) -> None:
        result = NLUResult.model_validate(
            {
                "intent": "view_child_attendance",
                "language": "en",
                "entities": {},
                "missing_information": ["student_identifier"],
                "confidence": 0.85,
            }
        )
        self.assertEqual(result.missing_information, ["student_identifier"])

    def test_unsupported_language_is_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            NLUResult.model_validate(
                {
                    "intent": "unknown",
                    "language": "fr",
                    "entities": {},
                    "missing_information": [],
                    "confidence": 0.2,
                }
            )
