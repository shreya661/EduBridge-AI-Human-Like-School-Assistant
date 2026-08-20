"""High-level NLU service combining classification, context, and secure routing."""

from typing import Dict, Any, Optional
from app.nlu.models import IntentType
from app.nlu.intents import Intent
from app.nlu.schemas import NLUResult, NLUEntities
from app.nlu.classifier import NLUClassifier
from app.domain import school_domain_service
from app.session.models import Identity, Role
from app.authz.guard import authorize_request_detailed
from app.attendance.service import attendance_service


class NLUService:
    def __init__(self):
        self.classifier = NLUClassifier()
    
    def process_natural_language(
        self, 
        text: str, 
        identity: Identity,
        conversation_context: Optional[Dict[str, Any]] = None
    ) -> NLUResult:
        """
        Process natural language input with context
        """
        nlu_result = self.classifier.classify(text)
        
        # If user is a Parent and intent resolved to VIEW_OWN_ATTENDANCE or mentions child, map to VIEW_CHILD_ATTENDANCE
        if identity and identity.role == Role.PARENT:
            if nlu_result.intent == Intent.VIEW_OWN_ATTENDANCE:
                nlu_result.intent = Intent.VIEW_CHILD_ATTENDANCE
            
            if nlu_result.intent == Intent.VIEW_CHILD_ATTENDANCE:
                children = school_domain_service.get_children_for_parent(identity.user_id)
                if len(children) == 1 and not nlu_result.entities.student_name:
                    nlu_result.entities.student_name = children[0].name
                    nlu_result.entities.student_id = children[0].student_id
                    nlu_result.requires_clarification = False
                elif len(children) > 1 and not nlu_result.entities.student_name:
                    nlu_result.requires_clarification = True

        if conversation_context:
            nlu_result = self._apply_context(nlu_result, conversation_context)
        
        return nlu_result
    
    def _apply_context(self, nlu_result: NLUResult, context: Dict[str, Any]) -> NLUResult:
        """
        Apply conversation context to enhance entity resolution
        """
        if 'previous_intent' in context:
            prev_intent = context['previous_intent']
            if prev_intent in [Intent.VIEW_CHILD_ATTENDANCE, "view_child_attendance"]:
                if 'last' in getattr(nlu_result, "original_text", "").lower():
                    if not nlu_result.entities.date:
                        nlu_result.entities.date = 'last_month'
        
        if 'current_student' in context and not nlu_result.entities.student_name:
            nlu_result.entities.student_name = context['current_student']
        
        return nlu_result
    
    def route_to_tool(
        self,
        nlu_result: NLUResult,
        identity: Identity,
        conversation_id: str = ""
    ) -> Dict[str, Any]:
        """
        Route processed NLU result to appropriate tool with authorization
        """
        target_data = self._build_target_data(nlu_result, identity)
        
        intent_str = nlu_result.intent.value if hasattr(nlu_result.intent, "value") else str(nlu_result.intent)
        auth_result = authorize_request_detailed(identity, intent_str, target_data)
        
        if not auth_result.allowed:
            return {
                "success": False,
                "error": "Unauthorized",
                "message": "You don't have permission to perform this action.",
                "auth_result": auth_result
            }
        
        return self._execute_tool_route(nlu_result, identity, target_data)
    
    def _build_target_data(self, nlu_result: NLUResult, identity: Optional[Identity] = None) -> Dict[str, Any]:
        """
        Build target data for authorization from NLU result scoped to caller identity
        """
        target_data = {}
        
        if nlu_result.entities.student_id:
            target_data["target_student_id"] = nlu_result.entities.student_id
        elif nlu_result.entities.student_name:
            norm = nlu_result.entities.student_name.lower().strip()
            
            # Scoped lookup for parent
            if identity and identity.role == Role.PARENT:
                children = school_domain_service.get_children_for_parent(identity.user_id)
                match = next((c for c in children if norm in c.name.lower() or c.name.lower() in norm), None)
                if match:
                    target_data["target_student_id"] = match.student_id

            # Scoped lookup for teacher
            if not target_data.get("target_student_id") and identity and identity.role == Role.TEACHER:
                classes = school_domain_service.get_classes_for_teacher(identity.user_id)
                for cl in classes:
                    students = school_domain_service.get_students_in_class(cl.class_id)
                    match = next((s for s in students if norm in s.name.lower() or s.name.lower() in norm), None)
                    if match:
                        target_data["target_student_id"] = match.student_id
                        target_data["target_class_id"] = cl.class_id
                        break

            # Fallback domain lookup
            if not target_data.get("target_student_id"):
                students = school_domain_service.student_repo.get_all_students()
                for student in students:
                    if norm in student.name.lower() or student.name.lower() in norm:
                        target_data["target_student_id"] = student.student_id
                        break
        
        if nlu_result.entities.class_id:
            target_data["target_class_id"] = nlu_result.entities.class_id
        elif nlu_result.entities.class_name:
            classes = school_domain_service.class_repo.get_all_classes()
            for class_ in classes:
                if nlu_result.entities.class_name.lower() in class_.name.lower():
                    target_data["target_class_id"] = class_.class_id
                    break
        
        return target_data
    
    def _execute_tool_route(self, nlu_result: NLUResult, identity: Identity, target_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the appropriate tool based on intent
        """
        intent = nlu_result.intent
        
        try:
            if intent in [Intent.VIEW_OWN_ATTENDANCE, "view_own_attendance"]:
                student_id = identity.user_id
                records = attendance_service.get_attendance_by_student(student_id, identity)
                return {
                    "success": True,
                    "intent": intent.value if hasattr(intent, "value") else intent,
                    "data": [record.model_dump() if hasattr(record, "model_dump") else record.dict() for record in records],
                    "message": f"You have {len(records)} attendance records."
                }
            
            elif intent in [Intent.VIEW_CHILD_ATTENDANCE, "view_child_attendance"]:
                student_id = target_data.get("target_student_id")
                if not student_id:
                    return {
                        "success": False,
                        "error": "student_not_found",
                        "message": "Could not identify the student."
                    }
                
                records = attendance_service.get_attendance_by_student(student_id, identity)
                return {
                    "success": True,
                    "intent": intent.value if hasattr(intent, "value") else intent,
                    "data": [record.model_dump() if hasattr(record, "model_dump") else record.dict() for record in records],
                    "message": f"The student has {len(records)} attendance records."
                }
            
            elif intent in [Intent.MARK_ATTENDANCE, "mark_attendance"]:
                student_id = target_data.get("target_student_id")
                if not student_id:
                    return {
                        "success": False,
                        "error": "student_not_found",
                        "message": "Could not identify the student to mark attendance for."
                    }
                
                from datetime import date
                from app.attendance.models import AttendanceStatus
                
                status = nlu_result.entities.attendance_status or "PRESENT"
                try:
                    status_enum = AttendanceStatus[status]
                except KeyError:
                    status_enum = AttendanceStatus.PRESENT
                
                class_id = target_data.get("target_class_id") or "C001"
                record = attendance_service.record_attendance(
                    student_id=student_id,
                    class_id=class_id,
                    date=date.today(),
                    status=status_enum,
                    recorded_by=identity.user_id,
                    identity=identity
                )
                
                return {
                    "success": True,
                    "intent": intent.value if hasattr(intent, "value") else intent,
                    "data": record.model_dump() if hasattr(record, "model_dump") else record.dict(),
                    "message": f"Attendance marked as {status.lower()} for the student."
                }
            
            elif intent in [Intent.ESCALATE_TO_TEACHER, "escalate_to_teacher", Intent.ESCALATE_TO_MANAGEMENT, "escalate_to_management"]:
                from app.tools.escalation_tool import escalation_tool
                target = "teacher" if "teacher" in str(intent).lower() else "management"
                esc_res = escalation_tool.execute(
                    identity=identity,
                    target=target,
                    reason="Callback requested via natural language assistant",
                    student_id=target_data.get("target_student_id")
                )
                return {
                    "success": esc_res.get("success", True),
                    "intent": intent.value if hasattr(intent, "value") else intent,
                    "data": esc_res,
                    "message": esc_res.get("message", f"Your request has been submitted to {target}.")
                }

            elif intent in [Intent.VIEW_SCHOOL_ANALYTICS, "view_school_analytics", Intent.VIEW_SCHOOL_ATTENDANCE, "view_school_attendance"]:
                from app.tools.analytics_tool import analytics_tool
                analytics_res = analytics_tool.execute(identity)
                return {
                    "success": analytics_res.get("success", True),
                    "intent": intent.value if hasattr(intent, "value") else intent,
                    "data": analytics_res.get("data"),
                    "message": analytics_res.get("message", "School analytics overview retrieved.")
                }

            elif intent in [Intent.GREETING, "greeting"]:
                role_display = identity.role.value.title()
                return {
                    "success": True,
                    "intent": intent.value if hasattr(intent, "value") else intent,
                    "message": f"Hello {identity.name}! You are logged in as {role_display}. How can I help you today?"
                }
            
            else:
                intent_val = intent.value if hasattr(intent, "value") else str(intent)
                return {
                    "success": True,
                    "intent": intent_val,
                    "message": f"Processing {intent_val.replace('_', ' ').title()} request..."
                }
        
        except Exception as e:
            return {
                "success": False,
                "error": "execution_error",
                "message": f"Error executing tool: {str(e)}"
            }


# Global instance
nlu_service = NLUService()
