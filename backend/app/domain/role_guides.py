"""Role Guidance and RBAC Capabilities reference dataset."""

from typing import Dict, Any, List
from pydantic import BaseModel


class RoleCapabilityGuide(BaseModel):
    role: str
    display_title: str
    icon: str
    color: str
    description: str
    primary_persona: str
    allowed_operations: List[str]
    prohibited_operations: List[str]
    sample_queries: List[str]
    zero_trust_boundary: str


ROLE_GUIDES_DATA: Dict[str, RoleCapabilityGuide] = {
    "STUDENT": RoleCapabilityGuide(
        role="STUDENT",
        display_title="Student Role",
        icon="🎓",
        color="#3d6b5e",
        description="Individual student learner profile with self-attendance tracking, timetable lookups, and direct teacher escalation.",
        primary_persona="Maya (Academic Specialist)",
        allowed_operations=[
            "View personal attendance record & overall %",
            "Check daily class timetable & upcoming exams",
            "Ask general school inquiries (holidays, timings, fees)",
            "Request 1-on-1 teacher consultation & callback tickets"
        ],
        prohibited_operations=[
            "Cannot view other students' personal records or grades",
            "Cannot mark or modify attendance records",
            "Cannot access administrative or school-wide analytics"
        ],
        sample_queries=[
            "What is my attendance?",
            "What is the timetable for tomorrow?",
            "Can I connect with my class teacher?",
            "Show me upcoming holidays"
        ],
        zero_trust_boundary="Self-record identity scoping strictly enforced via user_id token check."
    ),
    "PARENT": RoleCapabilityGuide(
        role="PARENT",
        display_title="Parent / Guardian Role",
        icon="👨‍👩‍👧",
        color="#7c3aed",
        description="Parent/guardian account with secure multi-child scoping, absence notifications, and teacher communication channels.",
        primary_persona="Dr. Priya (Counselor & Parent Liaison)",
        allowed_operations=[
            "View linked children's attendance records (Rahul, Arjun)",
            "Receive real-time WhatsApp / SMS absence alert simulations",
            "Request direct callback from class teachers or grade heads",
            "Check academic calendar and parent-teacher conference dates"
        ],
        prohibited_operations=[
            "Cannot access students outside their verified linked child set",
            "Cannot modify attendance or grading records",
            "Cannot access teacher staffing or confidential logs"
        ],
        sample_queries=[
            "How is Rahul's attendance?",
            "How is Arjun's attendance?",
            "I want to talk to my child's teacher",
            "When is the next parent-teacher conference?"
        ],
        zero_trust_boundary="Child-relationship verification checked in domain service before any data release."
    ),
    "TEACHER": RoleCapabilityGuide(
        role="TEACHER",
        display_title="Teacher / Educator Role",
        icon="👩‍🏫",
        color="#2563eb",
        description="Classroom educator dashboard for daily attendance marking, roster auditing, and student academic support.",
        primary_persona="Vikram (Senior Mentor)",
        allowed_operations=[
            "Mark students Present, Absent, Late, or Excused for assigned classes",
            "View Class 10-A and 10-B full attendance rosters",
            "Audit daily attendance submissions with real-time feedback",
            "Escalate safety or academic issues to school management"
        ],
        prohibited_operations=[
            "Cannot modify classes assigned to other educators",
            "Cannot change school-wide system or security settings",
            "Cannot view financial records or administrative budgets"
        ],
        sample_queries=[
            "Mark Rahul present today",
            "Mark Priya absent today",
            "Show Class 10-A attendance roster",
            "Escalate an issue to principal"
        ],
        zero_trust_boundary="Class assignment boundary checked against teacher course schedule table."
    ),
    "PRINCIPAL": RoleCapabilityGuide(
        role="PRINCIPAL",
        display_title="Principal / Administrator Role",
        icon="🏛️",
        color="#d97706",
        description="Institutional executive view with macro analytics, low-attendance interventions, and governance auditing.",
        primary_persona="Nova (Analytical Assistant)",
        allowed_operations=[
            "Access school-wide attendance analytics and KPI dashboards",
            "View flagged students (<75% attendance) and trigger interventions",
            "Audit all teacher submissions, escalation tickets, and logs",
            "Manage school calendar events, schedules, and policy rules"
        ],
        prohibited_operations=[
            "Audit trail cannot be deleted or forged (immutable logging)",
            "Zero-trust RBAC requires authenticated identity for every transaction"
        ],
        sample_queries=[
            "What is the overall attendance?",
            "Which students have low attendance?",
            "Show school attendance overview",
            "Generate monthly attendance report"
        ],
        zero_trust_boundary="Institutional executive access with complete audit logging on all queries."
    )
}
