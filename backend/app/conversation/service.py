"""Conversation orchestration over existing NLU, RBAC, ownership, and attendance layers."""

from typing import Protocol

from app.authz.guard import AuthorizationReason, is_allowed
from app.authz.ownership import validate_ownership
from app.conversation.manager import ConversationManager
from app.conversation.context import nlu_history
from app.conversation.persona import attendance_response
from app.conversation.schemas import ChatResponse, ConversationContext
from app.mock_api.attendance import find_student_by_name, identity_student_ids
from app.nlu.intents import Intent
from app.nlu.schemas import NLUEntities, NLUResult
from app.session.models import Identity
from app.tools.attendance_tool import AttendanceTool


class NLUAnalyzer(Protocol):
    async def analyze_message(self, message: str, conversation_context: list[dict] | None = None) -> NLUResult: ...


class ConversationService:
    def __init__(self, nlu: NLUAnalyzer, manager: ConversationManager | None = None, tool: AttendanceTool | None = None) -> None:
        self._nlu = nlu
        self._manager = manager or ConversationManager()
        self._tool = tool or AttendanceTool()

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
        permission = is_allowed(identity, intent)
        if not permission.allowed:
            return self._reply(context, intent, "I’m sorry, but I can’t access that information with your current account permissions.")

        if intent not in {Intent.VIEW_OWN_ATTENDANCE, Intent.VIEW_CHILD_ATTENDANCE}:
            return self._reply(context, intent, "I can help with attendance questions, but I need a more specific request.", True)

        if intent == Intent.VIEW_OWN_ATTENDANCE:
            if identity.student_id is None:
                return self._reply(context, intent, "I couldn't find your student record. Please contact the school office.")
            target_id = identity.student_id
        else:
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
            return self._reply(context, intent, "I couldn't find a student matching that name. Could you check the name and try again?")

        context.active_student_id = target_id
        context.last_intent = intent
        context.last_entities = nlu_result.entities
        context.last_tool = "attendance"
        context.last_verified_result = {key: value for key, value in result.items() if isinstance(value, (str, int, float))}
        context.requires_clarification = False
        context.clarification_question = None
        return self._reply(context, intent, attendance_response(identity.role, result))

    def _resolve_child(self, identity: Identity, entities: NLUEntities, context: ConversationContext) -> tuple[str | None, str | None]:
        target_id = entities.student_id
        if target_id is None and entities.student_name:
            record = find_student_by_name(entities.student_name)
            if record:
                numeric_id = record["student_id"]
                target_id = next((key for key, value in identity_student_ids.items() if value == numeric_id), None)
            else:
                return None, "I couldn't find a student matching that name. Could you check the name and try again?"
        if target_id is None:
            target_id = context.active_student_id
        if target_id is None and len(identity.associated_student_ids) == 1:
            target_id = identity.associated_student_ids[0]
        if target_id is None and len(identity.associated_student_ids) > 1:
            names = [self._tool.get_student_attendance(student_id)["student_name"] for student_id in identity.associated_student_ids]
            return None, f"Sure. Which child would you like me to check — {' or '.join(names)}?"
        if target_id is None:
            return None, "Sure. Whose attendance would you like me to check?"
        return target_id, None

    @staticmethod
    def _resolve_follow_up(result: NLUResult, context: ConversationContext, message: str) -> NLUResult:
        if context.requires_clarification:
            selected_name = result.entities.student_name or message.strip()
            if find_student_by_name(selected_name):
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
