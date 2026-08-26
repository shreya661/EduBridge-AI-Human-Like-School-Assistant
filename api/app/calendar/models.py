"""Calendar domain models and static schedule definitions."""

from typing import List, Optional
from pydantic import BaseModel
from enum import StrEnum


class EventCategory(StrEnum):
    EXAM = "exam"
    HOLIDAY = "holiday"
    EVENT = "event"
    MEETING = "meeting"
    ACADEMIC = "academic"


class CalendarEvent(BaseModel):
    id: str
    title: str
    date: str
    category: EventCategory
    description: str
    badge_color: str
    applicable_roles: List[str]


class TimetablePeriod(BaseModel):
    period_num: int
    time_slot: str
    subject: str
    teacher_name: str
    room: str


class ClassTimetable(BaseModel):
    class_id: str
    class_name: str
    day: str
    periods: List[TimetablePeriod]


# Curated School Events Dataset
CALENDAR_EVENTS: List[CalendarEvent] = [
    CalendarEvent(
        id="EVT-001",
        title="Mid-Term Mathematics & Science Exams",
        date="2026-09-05",
        category=EventCategory.EXAM,
        description="Comprehensive assessments for Grades 9 and 10 in Hall A and B.",
        badge_color="#ef4444",
        applicable_roles=["STUDENT", "TEACHER", "PARENT", "PRINCIPAL"]
    ),
    CalendarEvent(
        id="EVT-002",
        title="Teacher-Parent Conference (Term 1 Review)",
        date="2026-09-12",
        category=EventCategory.MEETING,
        description="One-on-one progress review between subject teachers and parents.",
        badge_color="#8b5cf6",
        applicable_roles=["PARENT", "TEACHER", "PRINCIPAL"]
    ),
    CalendarEvent(
        id="EVT-003",
        title="Ganesh Chaturthi School Holiday",
        date="2026-09-15",
        category=EventCategory.HOLIDAY,
        description="School will remain closed for all students and academic staff.",
        badge_color="#10b981",
        applicable_roles=["STUDENT", "TEACHER", "PARENT", "PRINCIPAL"]
    ),
    CalendarEvent(
        id="EVT-004",
        title="Annual Inter-House Science & Robotics Exhibition",
        date="2026-09-22",
        category=EventCategory.EVENT,
        description="Student project showcase in the school auditorium from 9:00 AM to 3:00 PM.",
        badge_color="#3b82f6",
        applicable_roles=["STUDENT", "TEACHER", "PARENT", "PRINCIPAL"]
    ),
    CalendarEvent(
        id="EVT-005",
        title="Gandhi Jayanti Public Holiday",
        date="2026-10-02",
        category=EventCategory.HOLIDAY,
        description="National holiday. School operations and offices suspended.",
        badge_color="#10b981",
        applicable_roles=["STUDENT", "TEACHER", "PARENT", "PRINCIPAL"]
    ),
    CalendarEvent(
        id="EVT-006",
        title="Quarterly Attendance & Academic Audit",
        date="2026-10-10",
        category=EventCategory.ACADEMIC,
        description="Principal and administrative staff review low-attendance alerts and intervention plans.",
        badge_color="#f59e0b",
        applicable_roles=["PRINCIPAL", "TEACHER"]
    ),
    CalendarEvent(
        id="EVT-007",
        title="Diwali Break & Festival Holidays",
        date="2026-11-02",
        category=EventCategory.HOLIDAY,
        description="School closed for 3 days for Diwali festivities.",
        badge_color="#10b981",
        applicable_roles=["STUDENT", "TEACHER", "PARENT", "PRINCIPAL"]
    ),
    CalendarEvent(
        id="EVT-008",
        title="Term 1 Final Examination Series",
        date="2026-11-20",
        category=EventCategory.EXAM,
        description="Term-end comprehensive summative examinations across all academic subjects.",
        badge_color="#ef4444",
        applicable_roles=["STUDENT", "TEACHER", "PARENT", "PRINCIPAL"]
    ),
    CalendarEvent(
        id="EVT-009",
        title="Annual Sports Day & Athletics Meet",
        date="2026-12-15",
        category=EventCategory.EVENT,
        description="Inter-house track & field competitions, athletics, and cultural drill displays.",
        badge_color="#3b82f6",
        applicable_roles=["STUDENT", "TEACHER", "PARENT", "PRINCIPAL"]
    ),
    CalendarEvent(
        id="EVT-010",
        title="Republic Day Flag Hoisting & Cultural Assembly",
        date="2027-01-26",
        category=EventCategory.EVENT,
        description="Ceremonial flag hoisting at 8:00 AM followed by national anthem and student performances.",
        badge_color="#3b82f6",
        applicable_roles=["STUDENT", "TEACHER", "PARENT", "PRINCIPAL"]
    ),
    CalendarEvent(
        id="EVT-011",
        title="Class 10 Board Examination Practicals & Vivas",
        date="2027-02-15",
        category=EventCategory.EXAM,
        description="External examiner assessments in Science Lab and Computer Science.",
        badge_color="#ef4444",
        applicable_roles=["STUDENT", "TEACHER", "PRINCIPAL"]
    )
]

# Timetable dataset for Class 10-A, 10-B, and 9-A
TIMETABLES = {
    "10-A": ClassTimetable(
        class_id="10-A",
        class_name="Class 10-A (Secondary)",
        day="Monday – Friday",
        periods=[
            TimetablePeriod(period_num=1, time_slot="08:30 - 09:15 AM", subject="Mathematics", teacher_name="Mr. Kumar Singh", room="Room 201"),
            TimetablePeriod(period_num=2, time_slot="09:15 - 10:00 AM", subject="Physics", teacher_name="Dr. Sunita Rao", room="Lab 2"),
            TimetablePeriod(period_num=3, time_slot="10:15 - 11:00 AM", subject="English Literature", teacher_name="Ms. Aarti Deshmukh", room="Room 201"),
            TimetablePeriod(period_num=4, time_slot="11:00 - 11:45 AM", subject="Computer Science / AI", teacher_name="Mr. Vikram Mehta", room="Comp Lab 1"),
            TimetablePeriod(period_num=5, time_slot="12:30 - 01:15 PM", subject="Social Studies", teacher_name="Mr. Rohan Gupta", room="Room 201"),
            TimetablePeriod(period_num=6, time_slot="01:15 - 02:00 PM", subject="Physical Education", teacher_name="Coach Sandeep", room="Ground A"),
        ]
    ),
    "10-B": ClassTimetable(
        class_id="10-B",
        class_name="Class 10-B (Secondary)",
        day="Monday – Friday",
        periods=[
            TimetablePeriod(period_num=1, time_slot="08:30 - 09:15 AM", subject="English Literature", teacher_name="Ms. Aarti Deshmukh", room="Room 202"),
            TimetablePeriod(period_num=2, time_slot="09:15 - 10:00 AM", subject="Mathematics", teacher_name="Mr. Kumar Singh", room="Room 202"),
            TimetablePeriod(period_num=3, time_slot="10:15 - 11:00 AM", subject="Chemistry", teacher_name="Dr. Sunita Rao", room="Lab 3"),
            TimetablePeriod(period_num=4, time_slot="11:00 - 11:45 AM", subject="Hindi / Regional Lang", teacher_name="Pandit Sharma", room="Room 202"),
            TimetablePeriod(period_num=5, time_slot="12:30 - 01:15 PM", subject="Biology", teacher_name="Dr. Kavita Verma", room="Bio Lab"),
            TimetablePeriod(period_num=6, time_slot="01:15 - 02:00 PM", subject="Art & Design", teacher_name="Ms. Meera Sen", room="Art Room"),
        ]
    ),
    "9-A": ClassTimetable(
        class_id="9-A",
        class_name="Class 9-A (Foundation)",
        day="Monday – Friday",
        periods=[
            TimetablePeriod(period_num=1, time_slot="08:30 - 09:15 AM", subject="General Science", teacher_name="Dr. Sunita Rao", room="Lab 1"),
            TimetablePeriod(period_num=2, time_slot="09:15 - 10:00 AM", subject="Social Science", teacher_name="Mr. Rohan Gupta", room="Room 101"),
            TimetablePeriod(period_num=3, time_slot="10:15 - 11:00 AM", subject="Mathematics Foundation", teacher_name="Mr. Kumar Singh", room="Room 101"),
            TimetablePeriod(period_num=4, time_slot="11:00 - 11:45 AM", subject="English Grammar & Comp", teacher_name="Ms. Aarti Deshmukh", room="Room 101"),
            TimetablePeriod(period_num=5, time_slot="12:30 - 01:15 PM", subject="Environmental Science", teacher_name="Dr. Kavita Verma", room="Room 101"),
            TimetablePeriod(period_num=6, time_slot="01:15 - 02:00 PM", subject="Music & Performing Arts", teacher_name="Ms. Ritu Roy", room="Music Hall"),
        ]
    )
}
