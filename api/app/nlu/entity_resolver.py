"""Deterministic entity resolution against the school domain model."""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional
from app.domain.models import Student
from app.domain import student_repo
from app.mock_api.attendance import mock_attendance_data


class ResolutionStatus(str, Enum):
    EXACT_MATCH = "EXACT_MATCH"
    AMBIGUOUS_MATCH = "AMBIGUOUS_MATCH"
    NOT_FOUND = "NOT_FOUND"


@dataclass
class StudentResolution:
    status: ResolutionStatus
    student_id: Optional[str] = None
    student_name: Optional[str] = None
    candidates: Optional[List[Student]] = None
    clarification_message: Optional[str] = None


def resolve_student(
    student_name: Optional[str] = None,
    student_id: Optional[str] = None,
    allowed_student_ids: Optional[List[str]] = None
) -> StudentResolution:
    """
    Deterministically resolve student identity from domain data.
    Never guesses if multiple matches are found.
    """
    # 1. Direct student_id match
    if student_id:
        student = student_repo.get_student(student_id)
        if student:
            if allowed_student_ids is not None and student.student_id not in allowed_student_ids:
                return StudentResolution(status=ResolutionStatus.NOT_FOUND)
            return StudentResolution(
                status=ResolutionStatus.EXACT_MATCH,
                student_id=student.student_id,
                student_name=student.name
            )
        for item in mock_attendance_data:
            if str(item["student_id"]) == str(student_id):
                return StudentResolution(
                    status=ResolutionStatus.EXACT_MATCH,
                    student_id=str(item["student_id"]),
                    student_name=item["student_name"]
                )

    # 2. Student name match
    if student_name:
        normalized = student_name.strip().casefold()
        all_students = student_repo.get_all_students()

        # Check exact full name match first
        exact_matches = []
        for s in all_students:
            if s.name.casefold() == normalized:
                if allowed_student_ids is None or s.student_id in allowed_student_ids:
                    exact_matches.append(s)

        if len(exact_matches) == 1:
            return StudentResolution(
                status=ResolutionStatus.EXACT_MATCH,
                student_id=exact_matches[0].student_id,
                student_name=exact_matches[0].name
            )
        elif len(exact_matches) > 1:
            names = [s.name for s in exact_matches]
            return StudentResolution(
                status=ResolutionStatus.AMBIGUOUS_MATCH,
                candidates=exact_matches,
                clarification_message=f"I found multiple students named {student_name}. Did you mean {' or '.join(names)}?"
            )

        # Check prefix/first-name match
        prefix_matches = []
        for s in all_students:
            s_name = s.name.casefold()
            if s_name.startswith(normalized + " ") or s_name.split()[0] == normalized:
                if allowed_student_ids is None or s.student_id in allowed_student_ids:
                    prefix_matches.append(s)

        # Deduplicate matches by student_id
        unique_matches = {s.student_id: s for s in prefix_matches}.values()
        unique_matches = list(unique_matches)

        if len(unique_matches) == 1:
            return StudentResolution(
                status=ResolutionStatus.EXACT_MATCH,
                student_id=unique_matches[0].student_id,
                student_name=unique_matches[0].name
            )
        elif len(unique_matches) > 1:
            names = [s.name for s in unique_matches]
            return StudentResolution(
                status=ResolutionStatus.AMBIGUOUS_MATCH,
                candidates=unique_matches,
                clarification_message=f"I found multiple students named {student_name}. Did you mean {' or '.join(names)}?"
            )

        # Fallback to mock attendance data if domain students had no match
        mock_matches = []
        for item in mock_attendance_data:
            item_name = item["student_name"].casefold()
            if item_name == normalized or item_name.startswith(normalized + " "):
                fake_s = Student(
                    student_id=f"S00{item['student_id']}",
                    name=item["student_name"],
                    class_id=f"C00{item['class_id']}"
                )
                if allowed_student_ids is None or fake_s.student_id in allowed_student_ids:
                    mock_matches.append(fake_s)

        if len(mock_matches) == 1:
            return StudentResolution(
                status=ResolutionStatus.EXACT_MATCH,
                student_id=mock_matches[0].student_id,
                student_name=mock_matches[0].name
            )

        return StudentResolution(
            status=ResolutionStatus.NOT_FOUND,
            clarification_message=f"I couldn't find any student matching '{student_name}'. Could you verify the name and try again?"
        )

    return StudentResolution(
        status=ResolutionStatus.NOT_FOUND,
        clarification_message="Please specify the student name or ID."
    )
