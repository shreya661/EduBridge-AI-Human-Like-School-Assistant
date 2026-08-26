"""Small helpers for converting stored context into safe NLU input."""

from app.conversation.schemas import ConversationContext


def nlu_history(context: ConversationContext) -> list[dict[str, str]]:
    """Expose only conversational language, never identity, role, or permissions."""
    return [
        {"user": turn.user_message, "assistant": turn.assistant_message}
        for turn in context.turns
    ]
