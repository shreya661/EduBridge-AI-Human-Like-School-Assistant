"""
Chatbot router — Endpoints for the floating chat widget.
Provides knowledge base search, message processing, and suggestion chips.
"""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from app.chatbot.service import chatbot_service
from app.chatbot.knowledge_base import KNOWLEDGE_BASE, search_knowledge_base

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
    confidence: str = "medium"
    timestamp: str


class KnowledgeSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    top_k: int = Field(3, ge=1, le=10)


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/message", response_model=ChatResponse)
async def process_chat_message(payload: ChatMessage):
    """
    Process a user message from the floating chat widget.
    Returns AI response, knowledge sources, and suggestion chips.
    """
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
        confidence=result.get("confidence", "medium"),
        timestamp=datetime.now().isoformat(),
    )


@router.get("/suggestions")
async def get_suggestion_chips():
    """Return default quick-suggestion chips for the chat widget launcher."""
    return {
        "suggestions": chatbot_service.get_suggestions(),
        "categories": chatbot_service.get_knowledge_categories(),
    }


@router.post("/search")
async def search_knowledge(payload: KnowledgeSearchRequest):
    """
    Direct knowledge base search endpoint.
    Returns matching KB entries for a given query.
    """
    results = search_knowledge_base(payload.query, top_k=payload.top_k)
    if not results:
        return {
            "results": [],
            "count": 0,
            "message": "No matching knowledge entries found.",
        }
    return {
        "results": [
            {
                "id": r["id"],
                "topic": r["topic"],
                "category": r["category"],
                "question": r["question"],
                "answer": r["answer"],
            }
            for r in results
        ],
        "count": len(results),
    }


@router.get("/topics")
async def get_all_topics():
    """List all available knowledge base topics and categories."""
    topics = [
        {
            "id": entry["id"],
            "topic": entry["topic"],
            "category": entry["category"],
            "question": entry["question"],
        }
        for entry in KNOWLEDGE_BASE
    ]
    return {
        "topics": topics,
        "total": len(topics),
        "categories": chatbot_service.get_knowledge_categories(),
    }


@router.get("/health")
async def chatbot_health():
    """Health check for chatbot service."""
    return {
        "status": "ok",
        "service": "XYZ AI Chatbot",
        "knowledge_entries": len(KNOWLEDGE_BASE),
        "timestamp": datetime.now().isoformat(),
    }
