"""Contracts for the controlled conversation boundary."""

from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.nlu.intents import Intent
from app.nlu.schemas import NLUEntities
from app.session.models import Role


class ConversationTurn(BaseModel):
    model_config = ConfigDict(frozen=True)

    user_message: str = Field(min_length=1, max_length=4_000)
    assistant_message: str = Field(min_length=1)
    intent: Intent
    entities: NLUEntities = Field(default_factory=NLUEntities)
    tool_result: dict[str, str | float | int] | None = None


class ConversationContext(BaseModel):
    """Bounded data useful for interpreting the next turn; never an identity source."""

    model_config = ConfigDict(validate_assignment=True)

    conversation_id: str
    user_id: str
    trusted_role: Role
    active_student_id: str | None = None
    last_intent: Intent | None = None
    last_entities: NLUEntities = Field(default_factory=NLUEntities)
    last_tool: str | None = None
    last_verified_result: dict[str, str | float | int] | None = None
    requires_clarification: bool = False
    clarification_question: str | None = None
    turns: list[ConversationTurn] = Field(default_factory=list)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ChatRequest(BaseModel):
    """The request body deliberately carries no identity or role information."""

    model_config = ConfigDict(extra="forbid")

    conversation_id: str | None = Field(default=None, min_length=1, max_length=128)
    message: str = Field(min_length=1, max_length=4_000)


class ChatResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    conversation_id: str
    message: str
    intent: Intent
    requires_clarification: bool = False
