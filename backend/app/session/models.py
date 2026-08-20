# backend/app/session/models.py
from pydantic import BaseModel
from typing import Optional, List
from enum import Enum

class Role(str, Enum):
    STUDENT = "STUDENT"
    PARENT = "PARENT"
    TEACHER = "TEACHER"
    PRINCIPAL = "PRINCIPAL"

class Identity(BaseModel):
    user_id: str
    role: Role
    name: str
    student_id: Optional[str] = None
    associated_student_ids: List[str] = []
    assigned_class_names: List[str] = []
