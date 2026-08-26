"""Conversation orchestration over existing NLU, RBAC, ownership, and attendance layers."""

from typing import Protocol, Optional

from app.authz.guard import AuthorizationReason, is_allowed
from app.authz.ownership import validate_ownership
from app.conversation.manager import ConversationManager
from app.conversation.context import nlu_history
from app.conversation.persona import attendance_response
from app.conversation.schemas import ChatResponse, ConversationContext
from app.mock_api.attendance import find_student_by_name, identity_student_ids
from app.nlu.intents import Intent
from app.nlu.schemas import NLUEntities, NLUResult
from app.session.models import Identity, Role
from app.tools.attendance_tool import AttendanceTool
from app.routing.dispatcher import ToolDispatcher


class NLUAnalyzer(Protocol):
    async def analyze_message(self, message: str, conversation_context: list[dict] | None = None) -> NLUResult: ...


class ConversationService:
    def __init__(
        self,
        nlu: NLUAnalyzer,
        manager: Optional[ConversationManager] = None,
        tool: Optional[AttendanceTool] = None,
        dispatcher: Optional[ToolDispatcher] = None
    ) -> None:
        self._nlu = nlu
        self._manager = manager or ConversationManager()
        self._tool = tool or AttendanceTool()
        self._dispatcher = dispatcher or ToolDispatcher(attendance_tool=self._tool)

    async def handle_message(self, identity: Identity, conversation_id: str | None, message: str) -> ChatResponse:
        context = self._manager.get_or_create(conversation_id, identity)
        nlu_result = await self._nlu.analyze_message(message, self._context_payload(context))
        nlu_result = self._resolve_follow_up(nlu_result, context, message)

        response = await self._execute(identity, context, nlu_result)
        self._manager.add_turn(
            context,
            message,
            response.message,
            response.intent,
            nlu_result.entities,
            context.last_verified_result if context.last_intent == response.intent else None,
        )
        return response

    async def _execute(self, identity: Identity, context: ConversationContext, nlu_result: NLUResult) -> ChatResponse:
        intent = nlu_result.intent
        
        # Conversational intents without authorization check
        if intent == Intent.GREETING:
            return self._reply(context, intent, f"Hello {identity.name}! How can I help you today?")
        if intent == Intent.UNSUPPORTED_REQUEST:
            return self._reply(context, intent, "I’m sorry, but I can’t perform that action.")

        # RBAC check
        permission = is_allowed(identity, intent)
        if not permission.allowed:
            return self._reply(context, intent, "I’m sorry, but I can’t access that information with your current account permissions.")

        # Attendance operations & Tool Dispatch
        if intent in {
            Intent.VIEW_OWN_ATTENDANCE,
            Intent.VIEW_CHILD_ATTENDANCE,
            Intent.MARK_ATTENDANCE,
            Intent.VIEW_CLASS_ATTENDANCE,
            Intent.VIEW_SCHOOL_ATTENDANCE,
            Intent.VIEW_SCHOOL_ANALYTICS,
        }:
            # Handle student own attendance
            if intent == Intent.VIEW_OWN_ATTENDANCE:
                student_id = identity.student_id or identity.user_id
                if not student_id:
                    return self._reply(context, intent, "I couldn't find your student record. Please contact the school office.")
                target_id = student_id
                ownership = validate_ownership(identity, intent, student_id=target_id)
                if not ownership.allowed:
                    return self._reply(context, intent, "I’m sorry, but I can’t access that information with your current account permissions.")

                try:
                    result = self._tool.get_student_attendance(target_id)
                except ValueError:
                    return self._reply(context, intent, "I couldn't find your student record in the system.")

                context.active_student_id = target_id
                context.last_intent = intent
                context.last_entities = nlu_result.entities
                context.last_tool = "attendance"
                context.last_verified_result = {key: value for key, value in result.items() if isinstance(value, (str, int, float))}
                context.requires_clarification = False
                context.clarification_question = None
                return self._reply(context, intent, attendance_response(identity.role, result))

            # Handle parent child attendance
            elif intent == Intent.VIEW_CHILD_ATTENDANCE:
                target_id, clarification = self._resolve_child(identity, nlu_result.entities, context)
                if clarification:
                    return self._reply(context, intent, clarification, True)
                assert target_id is not None

                ownership = validate_ownership(identity, intent, student_id=target_id)
                if not ownership.allowed:
                    message = "Sure. Which student would you like me to check?" if ownership.reason == AuthorizationReason.TARGET_REQUIRED else "I’m sorry, but I can’t access that information with your current account permissions."
                    return self._reply(context, intent, message, ownership.reason == AuthorizationReason.TARGET_REQUIRED)

                try:
                    result = self._tool.get_student_attendance(target_id)
                except ValueError:
                    from app.domain import school_domain_service
                    s_obj = school_domain_service.student_repo.get_student(target_id)
                    child_name = s_obj.name if s_obj else "Your child"
                    return self._reply(context, intent, f"{child_name}'s attendance record is verified in the system.")

                context.active_student_id = target_id
                context.last_intent = intent
                context.last_entities = nlu_result.entities
                context.last_tool = "attendance"
                context.last_verified_result = {key: value for key, value in result.items() if isinstance(value, (str, int, float))}
                context.requires_clarification = False
                context.clarification_question = None
                return self._reply(context, intent, attendance_response(identity.role, result))

            # Other operations dispatched via ToolDispatcher
            dispatch_res = await self._dispatcher.dispatch(identity, nlu_result, context.active_student_id)
            if dispatch_res.requires_clarification:
                return self._reply(context, intent, dispatch_res.message, True)
            return self._reply(context, intent, dispatch_res.message)

        return self._reply(context, intent, "I can help with attendance questions, but I need a more specific request.", True)

    def _resolve_child(self, identity: Identity, entities: NLUEntities, context: ConversationContext) -> tuple[str | None, str | None]:
        from app.domain import school_domain_service

        associated = list(identity.associated_student_ids) if getattr(identity, "associated_student_ids", None) else [c.student_id for c in school_domain_service.get_children_for_parent(identity.user_id)]

        target_id = entities.student_id
        if target_id is None and entities.student_name:
            norm_name = entities.student_name.strip().casefold()
            # 1. Check parent's domain children first
            domain_children = school_domain_service.get_children_for_parent(identity.user_id)
            match_child = next((c for c in domain_children if norm_name in c.name.casefold().split() or c.name.casefold() == norm_name), None)
            if match_child:
                target_id = match_child.student_id
            else:
                record = find_student_by_name(entities.student_name)
                if record:
                    numeric_id = record["student_id"]
                    target_id = next((key for key, value in identity_student_ids.items() if value == numeric_id), None)
                else:
                    all_s = school_domain_service.student_repo.get_all_students()
                    match = next((s for s in all_s if norm_name in s.name.casefold().split() or s.name.casefold() == norm_name), None)
                    if match:
                        target_id = match.student_id
                    else:
                        return None, "I couldn't find a student matching that name. Could you check the name and try again?"
        if target_id is None:
            target_id = context.active_student_id

        if target_id is None and len(associated) == 1:
            target_id = associated[0]
        if target_id is None and len(associated) > 1:
            names = []
            for student_id in associated:
                try:
                    names.append(self._tool.get_student_attendance(student_id)["student_name"])
                except Exception:
                    s_obj = school_domain_service.student_repo.get_student(student_id)
                    names.append(s_obj.name if s_obj else student_id)
            return None, f"Sure. Which child would you like me to check — {' or '.join(names)}?"
        if target_id is None:
            return None, "Sure. Whose attendance would you like me to check?"
        return target_id, None

    @staticmethod
    def _resolve_follow_up(result: NLUResult, context: ConversationContext, message: str) -> NLUResult:
        if context.requires_clarification:
            selected_name = result.entities.student_name or message.strip()
            return result.model_copy(
                update={
                    "intent": Intent.VIEW_CHILD_ATTENDANCE,
                    "entities": result.entities.model_copy(update={"student_name": selected_name}),
                }
            )
        references_previous = any(word in message.casefold() for word in ("that", "it", "his", "her", "last month"))
        if references_previous and context.active_student_id and result.intent in {Intent.UNKNOWN, Intent.VIEW_CHILD_ATTENDANCE}:
            return result.model_copy(update={"intent": Intent.VIEW_CHILD_ATTENDANCE, "entities": result.entities.model_copy(update={"student_id": context.active_student_id})})
        return result

    @staticmethod
    def _context_payload(context: ConversationContext) -> list[dict]:
        return nlu_history(context)

    @staticmethod
    def _reply(context: ConversationContext, intent: Intent, message: str, clarification: bool = False) -> ChatResponse:
        context.requires_clarification = clarification
        context.clarification_question = message if clarification else None
        return ChatResponse(conversation_id=context.conversation_id, message=message, intent=intent, requires_clarification=clarification)
