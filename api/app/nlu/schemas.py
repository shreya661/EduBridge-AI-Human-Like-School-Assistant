"""Validated data contracts for NLU input and output."""

from typing import Any, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.nlu.intents import Intent


SUPPORTED_LANGUAGE_CODES = {
    "en",
    "hi",
    "ta",
    "te",
    "mr",
    "bn",
    "gu",
    "pa",
    "kn",
    "ml",
    "ur",
    "unknown",
}


class NLUEntities(BaseModel):
    """Optional entities extracted from a user message."""

    model_config = ConfigDict(extra="forbid")

    student_id: Optional[str] = None
    student_name: Optional[str] = None
    class_id: Optional[str] = None
    class_name: Optional[str] = None
    date: Optional[str] = None
    date_range: Optional[str] = None
    attendance_status: Optional[str] = None
    attendance_period: Optional[str] = None

    @property
    def date_expression(self) -> Optional[str]:
        return self.date

    @date_expression.setter
    def date_expression(self, value: Optional[str]) -> None:
        self.date = value



class NLUResult(BaseModel):
    """Trusted, validated interpretation of an untrusted model response."""

    model_config = ConfigDict(extra="forbid")

    intent: Intent
    language: str = "en"
    entities: NLUEntities = Field(default_factory=NLUEntities)
    missing_information: list[str] = Field(default_factory=list)
    requires_clarification: bool = False
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)

    @field_validator("language")
    @classmethod
    def validate_language(cls, value: str) -> str:
        if value not in SUPPORTED_LANGUAGE_CODES:
            raise ValueError("language must be a supported code or 'unknown'")
        return value


class NLUAnalyzeRequest(BaseModel):
    """Input accepted by the development NLU endpoint."""

    model_config = ConfigDict(extra="forbid")

    message: str = Field(min_length=1, max_length=4_000)
    conversation_context: list[dict[str, Any]] | None = None

    @field_validator("message")
    @classmethod
    def message_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("message must not be blank")
        return value
