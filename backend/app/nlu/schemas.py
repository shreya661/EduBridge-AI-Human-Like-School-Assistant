"""Validated data contracts for NLU input and output."""

from typing import Any

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

    model_config = ConfigDict(extra="forbid", strict=True)

    student_id: str | None = None
    student_name: str | None = None
    class_name: str | None = None
    date: str | None = None
    attendance_period: str | None = None


class NLUResult(BaseModel):
    """Trusted, validated interpretation of an untrusted model response."""

    model_config = ConfigDict(extra="forbid")

    intent: Intent
    language: str
    entities: NLUEntities = Field(default_factory=NLUEntities)
    missing_information: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0, strict=True)

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
