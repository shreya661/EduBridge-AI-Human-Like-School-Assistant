"""Trusted identity models supplied by the application session layer."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class Role(StrEnum):
    STUDENT = "student"
    PARENT = "parent"
    TEACHER = "teacher"
    PRINCIPAL = "principal"


class Identity(BaseModel):
    """Trusted identity data; never derive these fields from an LLM or message."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    user_id: str = Field(min_length=1)
    role: Role
    name: str = Field(min_length=1)
    student_id: str | None = None
    associated_student_ids: tuple[str, ...] = ()
    assigned_class_names: tuple[str, ...] = ()
