"""Centralized, deterministic tool routing and execution dispatcher."""

from dataclasses import dataclass
from typing import Any, Dict, Optional
from datetime import date

from app.nlu.intents import Intent
from app.nlu.schemas import NLUResult
from app.nlu.date_resolver import resolve_date_expression
from app.nlu.entity_resolver import resolve_student, ResolutionStatus
from app.session.models import Identity, Role
from app.authz.engine import AuthorizationEngine
from app.authz.models import AuthorizationDecision
from app.domain import school_domain_service
from app.tools.attendance_tool import AttendanceTool
from app.tools.escalation_tool import escalation_tool
from app.tools.analytics_tool import analytics_tool
from app.attendance.service import attendance_service
from app.attendance.models import AttendanceStatus


@dataclass
class DispatchResult:
    success: bool
    message: str
    intent: Intent
    data: Optional[Any] = None
    requires_clarification: bool = False
    clarification_question: Optional[str] = None


class ToolDispatcher:
    """
    Executes tool operations strictly AFTER authorization and entity resolution.
    Never executes arbitrary dynamic functions from LLM output.
    """

    def __init__(self, auth_engine: Optional[AuthorizationEngine] = None, attendance_tool: Optional[AttendanceTool] = None):
        self.auth_engine = auth_engine or AuthorizationEngine()
        self.attendance_tool = attendance_tool or AttendanceTool()

    async def dispatch(
        self,
        identity: Identity,
        nlu_result: NLUResult,
        context_active_student_id: Optional[str] = None
    ) -> DispatchResult:
        intent = nlu_result.intent
        entities = nlu_result.entities

        # 1. Non-tool conversational intents
        if intent == Intent.GREETING:
            return DispatchResult(
                success=True,
                message=f"Hello {identity.name}! How can I help you today?",
                intent=intent
            )

        if intent == Intent.UNSUPPORTED_REQUEST:
            return DispatchResult(
                success=False,
                message="I’m sorry, but I can’t perform that action.",
                intent=intent
            )

        if intent == Intent.CLARIFICATION_NEEDED or intent == Intent.UNKNOWN:
            missing = ", ".join(nlu_result.missing_information) if nlu_result.missing_information else "more details"
            return DispatchResult(
                success=False,
                message=f"Could you please provide {missing}?",
                intent=intent,
                requires_clarification=True,
                clarification_question=f"Could you please provide {missing}?"
            )

        # 2. Intent: VIEW_OWN_ATTENDANCE
        if intent == Intent.VIEW_OWN_ATTENDANCE:
            student_id = identity.student_id or identity.user_id
            auth_res = self.auth_engine.authorize_request(
                identity,
                "view_own_attendance",
                {"target_student_id": student_id}
            )
            if auth_res.decision != AuthorizationDecision.ALLOWED:
                return DispatchResult(
                    success=False,
                    message="I’m sorry, but I can’t access that information with your current account permissions.",
                    intent=intent
                )

            try:
                data = self.attendance_tool.get_student_attendance(student_id)
                pct = data.get("attendance_percentage", 0.0)
                return DispatchResult(
                    success=True,
                    message=f"Your current attendance is {pct:.1f}%.",
                    intent=intent,
                    data=data
                )
            except Exception:
                records = school_domain_service.get_attendance_for_student(student_id)
                return DispatchResult(
                    success=True,
                    message=f"You have {len(records)} recorded attendance sessions.",
                    intent=intent,
                    data=records
                )

        # 3. Intent: VIEW_CHILD_ATTENDANCE
        if intent == Intent.VIEW_CHILD_ATTENDANCE:
            children = school_domain_service.get_children_for_parent(identity.user_id)
            child_ids = [c.student_id for c in children]

            target_id = entities.student_id
            if not target_id and entities.student_name:
                res = resolve_student(student_name=entities.student_name, allowed_student_ids=child_ids)
                if res.status == ResolutionStatus.AMBIGUOUS_MATCH:
                    return DispatchResult(
                        success=False,
                        message=res.clarification_message or "Which child would you like me to check?",
                        intent=intent,
                        requires_clarification=True,
                        clarification_question=res.clarification_message
                    )
                elif res.status == ResolutionStatus.EXACT_MATCH:
                    target_id = res.student_id
                else:
                    return DispatchResult(
                        success=False,
                        message=f"I couldn't find a record for '{entities.student_name}' linked to your parent account.",
                        intent=intent
                    )

            if not target_id and context_active_student_id in child_ids:
                target_id = context_active_student_id

            if not target_id:
                if len(children) == 1:
                    target_id = children[0].student_id
                elif len(children) > 1:
                    names = [c.name for c in children]
                    msg = f"Sure. Which child would you like me to check — {' or '.join(names)}?"
                    return DispatchResult(
                        success=False,
                        message=msg,
                        intent=intent,
                        requires_clarification=True,
                        clarification_question=msg
                    )
                else:
                    return DispatchResult(
                        success=False,
                        message="No student accounts are currently linked to your parent profile.",
                        intent=intent
                    )

            auth_res = self.auth_engine.authorize_request(
                identity,
                "view_child_attendance",
                {"target_student_id": target_id}
            )
            if auth_res.decision != AuthorizationDecision.ALLOWED:
                return DispatchResult(
                    success=False,
                    message="I’m sorry, but I can’t access that information with your current account permissions.",
                    intent=intent
                )

            try:
                data = self.attendance_tool.get_student_attendance(target_id)
                name = data.get("student_name", "Your child")
                pct = data.get("attendance_percentage", 0.0)
                return DispatchResult(
                    success=True,
                    message=f"{name}'s current attendance is {pct:.1f}%.",
                    intent=intent,
                    data=data
                )
            except Exception:
                child = school_domain_service.student_repo.get_student(target_id)
                child_name = child.name if child else "Your child"
                records = school_domain_service.get_attendance_for_student(target_id)
                return DispatchResult(
                    success=True,
                    message=f"{child_name} has {len(records)} recorded attendance sessions.",
                    intent=intent,
                    data=records
                )

        # 4. Intent: MARK_ATTENDANCE
        if intent == Intent.MARK_ATTENDANCE:
            auth_rbac = self.auth_engine.authorize_request(identity, "mark_attendance", None)
            if auth_rbac.decision != AuthorizationDecision.ALLOWED:
                return DispatchResult(
                    success=False,
                    message="I’m sorry, but you do not have permission to mark attendance.",
                    intent=intent
                )

            target_date = resolve_date_expression(entities.date) or date.today()
            raw_status = (entities.attendance_status or "ABSENT").upper()
            try:
                status_enum = AttendanceStatus[raw_status]
            except KeyError:
                status_enum = AttendanceStatus.ABSENT

            assigned_classes = school_domain_service.get_classes_for_teacher(identity.user_id)
            teacher_class_ids = [c.class_id for c in assigned_classes]
            
            allowed_student_ids = []
            for cid in teacher_class_ids:
                allowed_student_ids.extend([s.student_id for s in school_domain_service.get_students_in_class(cid)])

            student_res = resolve_student(
                student_name=entities.student_name,
                student_id=entities.student_id,
                allowed_student_ids=allowed_student_ids if identity.role == Role.TEACHER else None
            )

            if student_res.status == ResolutionStatus.AMBIGUOUS_MATCH:
                return DispatchResult(
                    success=False,
                    message=student_res.clarification_message or "Which student should I mark?",
                    intent=intent,
                    requires_clarification=True,
                    clarification_question=student_res.clarification_message
                )
            elif student_res.status != ResolutionStatus.EXACT_MATCH:
                return DispatchResult(
                    success=False,
                    message=f"I couldn't find a student named '{entities.student_name}' in your assigned classes.",
                    intent=intent
                )

            target_student_id = student_res.student_id
            student_obj = school_domain_service.student_repo.get_student(target_student_id)
            class_id = student_obj.class_id if student_obj else "C001"

            auth_res = self.auth_engine.authorize_request(
                identity,
                "mark_attendance",
                {"target_student_id": target_student_id, "target_class_id": class_id}
            )
            if auth_res.decision != AuthorizationDecision.ALLOWED:
                return DispatchResult(
                    success=False,
                    message="I’m sorry, but you do not have permission to mark attendance for this student.",
                    intent=intent
                )

            record = attendance_service.record_attendance(
                student_id=target_student_id,
                class_id=class_id,
                date=target_date,
                status=status_enum,
                recorded_by=identity.user_id,
                identity=identity
            )
            return DispatchResult(
                success=True,
                message=f"Successfully marked {student_res.student_name} as {status_enum.value} for {target_date.isoformat()}.",
                intent=intent,
                data=record
            )

        # 5. Intent: VIEW_CLASS_ATTENDANCE
        if intent == Intent.VIEW_CLASS_ATTENDANCE:
            class_id = entities.class_id or "C001"
            auth_res = self.auth_engine.authorize_request(
                identity,
                "view_class_roster",
                {"target_class_id": class_id}
            )
            if auth_res.decision != AuthorizationDecision.ALLOWED:
                return DispatchResult(
                    success=False,
                    message="I’m sorry, but I can’t access attendance for that class.",
                    intent=intent
                )

            records = school_domain_service.get_attendance_for_class(class_id)
            return DispatchResult(
                success=True,
                message=f"Class {class_id} has {len(records)} attendance records.",
                intent=intent,
                data=records
            )

        # 6. Intent: VIEW_SCHOOL_ATTENDANCE
        if intent == Intent.VIEW_SCHOOL_ATTENDANCE:
            auth_res = self.auth_engine.authorize_request(
                identity,
                "view_all_attendance"
            )
            if auth_res.decision != AuthorizationDecision.ALLOWED:
                return DispatchResult(
                    success=False,
                    message="I’m sorry, but I can’t access that information with your current account permissions.",
                    intent=intent
                )

            school_records = self.attendance_tool.view_school_attendance()
            total = len(school_records)
            return DispatchResult(
                success=True,
                message=f"Overall school attendance across {total} student cohorts is tracked.",
                intent=intent,
                data=school_records
            )

        # 7. Intent: VIEW_SCHOOL_ANALYTICS
        if intent == Intent.VIEW_SCHOOL_ANALYTICS:
            auth_res = self.auth_engine.authorize_request(
                identity,
                "view_school_analytics"
            )
            if auth_res.decision != AuthorizationDecision.ALLOWED:
                return DispatchResult(
                    success=False,
                    message="I’m sorry, but I can’t access school analytics with your current account permissions.",
                    intent=intent
                )

            res = analytics_tool.execute(identity)
            return DispatchResult(
                success=res.get("success", True),
                message=res.get("message", "School analytics loaded."),
                intent=intent,
                data=res.get("data")
            )

        # 8. Intent: ESCALATE_TO_TEACHER or ESCALATE_TO_MANAGEMENT
        if intent in {Intent.ESCALATE_TO_TEACHER, Intent.ESCALATE_TO_MANAGEMENT}:
            target_str = "teacher" if intent == Intent.ESCALATE_TO_TEACHER else "management"
            auth_op = f"escalate_to_{target_str}"
            auth_res = self.auth_engine.authorize_request(identity, auth_op)
            if auth_res.decision != AuthorizationDecision.ALLOWED:
                return DispatchResult(
                    success=False,
                    message="I’m sorry, but you do not have permission to escalate this request.",
                    intent=intent
                )

            res = escalation_tool.execute(
                identity=identity,
                target=target_str,
                reason="Callback requested via assistant",
                student_id=entities.student_id
            )
            return DispatchResult(
                success=res.get("success", True),
                message=res.get("message", "Escalation ticket created."),
                intent=intent,
                data=res
            )

        # Fallback for unhandled intent
        return DispatchResult(
            success=False,
            message="I’m sorry, I cannot process that request at this time.",
            intent=intent
        )
