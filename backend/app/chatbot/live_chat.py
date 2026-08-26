"""
In-memory live chat session manager.
Handles student/parent → teacher/admin live chat sessions inside the floating widget.
Upgradeable to DB-backed sessions later.
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum


class SessionStatus(str, Enum):
    PENDING = "pending"      # Waiting for teacher to accept
    ACTIVE = "active"        # Live chat in progress
    CLOSED = "closed"        # Session ended


class LiveMessage:
    def __init__(self, sender: str, sender_role: str, text: str):
        self.id = str(uuid.uuid4())[:8]
        self.sender = sender
        self.sender_role = sender_role    # "student", "parent", "teacher", "system"
        self.text = text
        self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "sender": self.sender,
            "sender_role": self.sender_role,
            "text": self.text,
            "timestamp": self.timestamp
        }


class LiveChatSession:
    def __init__(self, requester_id: str, requester_role: str,
                 target_role: str, reason: str):
        self.session_id = str(uuid.uuid4())[:12]
        self.requester_id = requester_id
        self.requester_role = requester_role   # "student" or "parent"
        self.target_role = target_role         # "teacher" or "admin"
        self.reason = reason
        self.status = SessionStatus.PENDING
        self.messages: List[LiveMessage] = []
        self.created_at = datetime.now().isoformat()

        # Add system welcome message
        self._add_system_message(
            f"Chat request received — connecting you to a {target_role}. "
            f"Reason: '{reason}'. Please wait a moment..."
        )

    def _add_system_message(self, text: str):
        msg = LiveMessage("System", "system", text)
        self.messages.append(msg)

    def add_message(self, sender: str, sender_role: str, text: str) -> LiveMessage:
        msg = LiveMessage(sender, sender_role, text)
        self.messages.append(msg)
        return msg

    def accept(self, teacher_name: str = "Ms. Priya Sharma"):
        """Mark session as active (teacher accepted)."""
        self.status = SessionStatus.ACTIVE
        self._add_system_message(
            f"✅ {teacher_name} has joined the chat. You can now send your message!"
        )

    def close(self):
        self.status = SessionStatus.CLOSED
        self._add_system_message("Chat session ended. Thank you for using XYZ AI Live Chat! 👋")

    def to_dict(self) -> Dict:
        return {
            "session_id": self.session_id,
            "requester_id": self.requester_id,
            "requester_role": self.requester_role,
            "target_role": self.target_role,
            "reason": self.reason,
            "status": self.status,
            "messages": [m.to_dict() for m in self.messages],
            "created_at": self.created_at
        }


# ── In-memory session store ────────────────────────────────────────────────────
_sessions: Dict[str, LiveChatSession] = {}

# Teacher auto-reply templates for demo simulation
_TEACHER_AUTO_REPLIES = [
    "Hello! I can see your request. How can I help you today?",
    "Thank you for reaching out. I'm looking at your records now.",
    "I understand your concern. Let me check with the administration and get back to you.",
    "Please don't worry — I'll make a note of this and we can discuss further in school tomorrow.",
    "Is there anything else I can help you with? Remember, you can always visit me during office hours (10 AM – 12 PM)."
]


def create_session(requester_id: str, requester_role: str,
                   target_role: str, reason: str) -> LiveChatSession:
    """Create a new live chat session."""
    session = LiveChatSession(requester_id, requester_role, target_role, reason)
    _sessions[session.session_id] = session
    return session


def get_session(session_id: str) -> Optional[LiveChatSession]:
    """Retrieve a session by ID."""
    return _sessions.get(session_id)


def get_messages_since(session_id: str, after_index: int = 0) -> List[Dict]:
    """Return messages after a given index for polling."""
    session = _sessions.get(session_id)
    if not session:
        return []
    return [m.to_dict() for m in session.messages[after_index:]]


def simulate_teacher_accept(session_id: str) -> bool:
    """Simulate a teacher accepting the session (for demo)."""
    session = _sessions.get(session_id)
    if session and session.status == SessionStatus.PENDING:
        session.accept()
        return True
    return False


def simulate_teacher_reply(session_id: str, reply_index: int = 0) -> Optional[Dict]:
    """Simulate an auto-reply from the teacher (for demo)."""
    session = _sessions.get(session_id)
    if not session or session.status != SessionStatus.ACTIVE:
        return None
    reply_text = _TEACHER_AUTO_REPLIES[reply_index % len(_TEACHER_AUTO_REPLIES)]
    msg = session.add_message("Ms. Priya Sharma", "teacher", reply_text)
    return msg.to_dict()


def close_session(session_id: str) -> bool:
    """Close a live chat session."""
    session = _sessions.get(session_id)
    if session:
        session.close()
        return True
    return False


def list_active_sessions() -> List[Dict]:
    """Return all non-closed sessions (admin view)."""
    return [s.to_dict() for s in _sessions.values() if s.status != SessionStatus.CLOSED]
