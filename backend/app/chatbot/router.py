"""
Chatbot router — Endpoints for the floating chat widget.
Provides knowledge base search, message processing, interactive quizzes,
exam countdowns, and live human-in-the-loop teacher chat sessions.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.chatbot.service import chatbot_service
from app.chatbot.knowledge_base import KNOWLEDGE_BASE, search_knowledge_base
from app.chatbot.quiz_data import get_quiz, list_quiz_topics, get_next_exam, STUDY_PLAN_WEEKS
from app.chatbot import live_chat

router = APIRouter(prefix="/api/v1/chatbot", tags=["chatbot"])


# ── Request / Response Models ─────────────────────────────────────────────────

class ChatMessage(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000, description="User message text")
    role: Optional[str] = Field("STUDENT", description="Current user role")
    conversation_id: Optional[str] = Field(None, description="Session conversation ID")


class ChatResponse(BaseModel):
    answer: str
    sources: List[dict] = []
    related_topics: List[str] = []
    suggestions: List[str] = []
    intent_hint: str = "general"
    quiz_data: Optional[Dict[str, Any]] = None
    countdown_data: Optional[Dict[str, Any]] = None
    confidence: str = "medium"
    timestamp: str


class LiveChatRequest(BaseModel):
    requester_id: str = Field(..., description="Student or Parent ID")
    requester_role: str = Field("STUDENT", description="Role of requester")
    target_role: str = Field("TEACHER", description="Teacher or Admin")
    reason: Optional[str] = Field("General inquiry", description="Reason for live chat")


class LiveSendRequest(BaseModel):
    sender: str
    sender_role: str
    text: str = Field(..., min_length=1, max_length=1000)


# ── Core Chatbot Endpoints ───────────────────────────────────────────────────

@router.post("/message", response_model=ChatResponse)
async def process_chat_message(payload: ChatMessage):
    """Process message from floating chat widget."""
    if not payload.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    result = chatbot_service.process_message(
        user_message=payload.message,
        role=payload.role or "STUDENT",
        conversation_history=[],
    )

    return ChatResponse(
        answer=result.get("answer", ""),
        sources=result.get("sources", []),
        related_topics=result.get("related_topics", []),
        suggestions=result.get("suggestions", []),
        intent_hint=result.get("intent_hint", "general"),
        quiz_data=result.get("quiz_data"),
        countdown_data=result.get("countdown_data"),
        confidence=result.get("confidence", "medium"),
        timestamp=datetime.now().isoformat(),
    )


@router.get("/suggestions")
async def get_suggestion_chips(mode: Optional[str] = Query("all", description="Mode pill")):
    """Return suggestion chips filtered by mode pill."""
    return {
        "mode": mode,
        "suggestions": chatbot_service.get_mode_chips(mode),
        "categories": chatbot_service.get_knowledge_categories(),
    }


# ── Quiz Endpoints ───────────────────────────────────────────────────────────

@router.get("/quiz-topics")
async def get_all_quiz_topics():
    """Return list of all available quiz topics."""
    return {"topics": list_quiz_topics()}


@router.get("/quiz/{topic}")
async def get_quiz_by_topic(topic: str):
    """Return 3 MCQs for a given topic."""
    quiz_obj = get_quiz(topic)
    if not quiz_obj:
        raise HTTPException(status_code=404, detail=f"No quiz found for topic '{topic}'.")
    return quiz_obj


# ── Exam Countdown Endpoint ──────────────────────────────────────────────────

@router.get("/exam-countdown")
async def get_exam_countdown():
    """Return next exam milestone and 4-week study planner."""
    next_exam = get_next_exam()
    if not next_exam:
        return {
            "has_upcoming": False,
            "message": "No exams currently scheduled in the active term."
        }
    return {
        "has_upcoming": True,
        "exam": next_exam,
        "study_plan": STUDY_PLAN_WEEKS
    }


# ── Live Chat Endpoints (Human-in-the-Loop) ───────────────────────────────────

@router.post("/live/request")
async def request_live_chat(payload: LiveChatRequest):
    """Initiate a live chat session with a teacher or admin."""
    session = live_chat.create_session(
        requester_id=payload.requester_id,
        requester_role=payload.requester_role.lower(),
        target_role=payload.target_role.lower(),
        reason=payload.reason or "General inquiry"
    )
    # Simulate teacher auto-accepting after initiation for demo
    live_chat.simulate_teacher_accept(session.session_id)

    return {
        "success": True,
        "session_id": session.session_id,
        "status": session.status,
        "message": f"Connected to {payload.target_role.title()} live chat channel.",
        "session": session.to_dict()
    }


@router.get("/live/{session_id}/messages")
async def get_live_messages(session_id: str, after: int = 0):
    """Poll for new messages in a live chat session."""
    session = live_chat.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Live chat session not found.")
    
    messages = live_chat.get_messages_since(session_id, after_index=after)
    return {
        "session_id": session_id,
        "status": session.status,
        "messages": messages,
        "total_messages": len(session.messages)
    }


@router.post("/live/{session_id}/send")
async def send_live_message(session_id: str, payload: LiveSendRequest):
    """Send a user message in the live chat session and simulate teacher reply."""
    session = live_chat.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Live chat session not found.")

    if session.status == live_chat.SessionStatus.CLOSED:
        raise HTTPException(status_code=400, detail="This chat session is closed.")

    msg = session.add_message(payload.sender, payload.sender_role, payload.text)

    # For demo simulation: if user sends a message, teacher replies
    teacher_reply = None
    if payload.sender_role in ["student", "parent"]:
        teacher_reply = live_chat.simulate_teacher_reply(session_id, reply_index=len(session.messages))

    return {
        "success": True,
        "message_sent": msg.to_dict(),
        "teacher_reply": teacher_reply
    }


@router.post("/live/{session_id}/close")
async def close_live_chat(session_id: str):
    """Close the active live chat session."""
    success = live_chat.close_session(session_id)
    return {"success": success, "message": "Live chat session closed."}


@router.get("/health")
async def chatbot_health():
    """Health check for chatbot service."""
    return {
        "status": "ok",
        "service": "XYZ AI Chatbot & Tutor",
        "knowledge_entries": len(KNOWLEDGE_BASE),
        "quiz_topics": len(list_quiz_topics()),
        "timestamp": datetime.now().isoformat(),
    }
