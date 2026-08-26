"""In-memory, bounded conversation storage for this MVP."""

from uuid import uuid4

from app.conversation.schemas import ConversationContext, ConversationTurn
from app.nlu.intents import Intent
from app.nlu.schemas import NLUEntities
from app.session.models import Identity


class ConversationAccessError(Exception):
    """Raised when a conversation is requested by a different authenticated user."""


class ConversationManager:
    def __init__(self, max_turns: int = 8) -> None:
        self._contexts: dict[str, ConversationContext] = {}
        self._max_turns = max_turns

    def get_or_create(self, conversation_id: str | None, identity: Identity) -> ConversationContext:
        if conversation_id is None:
            conversation_id = str(uuid4())
        context = self._contexts.get(conversation_id)
        if context is None:
            context = ConversationContext(
                conversation_id=conversation_id,
                user_id=identity.user_id,
                trusted_role=identity.role,
            )
            self._contexts[conversation_id] = context
        elif context.user_id != identity.user_id:
            raise ConversationAccessError("Conversation is not available for this user.")
        return context

    def add_turn(
        self,
        context: ConversationContext,
        user_message: str,
        assistant_message: str,
        intent: Intent,
        entities: NLUEntities,
        tool_result: dict[str, str | float | int] | None = None,
    ) -> None:
        context.turns.append(
            ConversationTurn(
                user_message=user_message,
                assistant_message=assistant_message,
                intent=intent,
                entities=entities,
                tool_result=tool_result,
            )
        )
        context.turns[:] = context.turns[-self._max_turns :]
