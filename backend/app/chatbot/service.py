"""
Chatbot service — handles knowledge base lookup, fallback responses,
and context-aware replies for the floating chat widget.
"""

from typing import List, Dict, Optional, Any
from datetime import datetime

from app.chatbot.knowledge_base import (
    search_knowledge_base,
    KNOWLEDGE_BASE,
)
from app.session.models import Role


GREETING_RESPONSES = [
    "👋 Hi there! I'm your XYZ AI School Assistant. Ask me anything — attendance, exam schedules, homework help, school policies, and more!",
    "😊 Hello! Ready to help! You can ask me about school timings, fee structure, exam dates, homework topics, or how to contact teachers.",
    "🎓 Hey! I'm XYZ AI. How can I help you today? Try asking about attendance rules, holidays, Newton's laws, or how to write an essay!",
]

FALLBACK_RESPONSE = (
    "🤔 I couldn't find a specific answer to your question in my knowledge base yet.\n\n"
    "Here are some things I **can** help you with:\n"
    "• 📋 School policies (timings, attendance rules, uniform, library)\n"
    "• 📝 Exam schedules and preparation tips\n"
    "• 💰 Fee structure and payment details\n"
    "• 🌿 Science concepts (photosynthesis, Newton's laws, cell biology)\n"
    "• ✍️ English essay writing tips\n"
    "• 📐 Maths — quadratic equations, formulas\n"
    "• 🏫 Admission, enrollment, and contact information\n\n"
    "You can also use the **main assistant** above to check attendance, mark students, or escalate issues!"
)

QUICK_SUGGESTION_CHIPS = [
    "School timings?",
    "Upcoming holidays?",
    "Attendance policy?",
    "Explain photosynthesis",
    "Newton's laws of motion",
    "How to write an essay?",
    "Fee structure?",
    "Exam schedule?",
    "Contact a teacher?",
]


class ChatbotService:
    """Floating chatbot widget service — Knowledge base lookup and response generation."""

    def process_message(
        self,
        user_message: str,
        role: Optional[str] = "STUDENT",
        conversation_history: Optional[List[Dict]] = None,
    ) -> Dict[str, Any]:
        """
        Process an incoming user message and return a structured chatbot response.

        Returns:
            dict with 'answer', 'sources', 'suggestions', 'intent_hint'
        """
        message_lower = user_message.lower().strip()

        # Handle greetings
        if self._is_greeting(message_lower):
            import random
            greeting = random.choice(GREETING_RESPONSES)
            return {
                "answer": greeting,
                "sources": [],
                "suggestions": QUICK_SUGGESTION_CHIPS[:5],
                "intent_hint": "greeting",
                "confidence": "high",
            }

        # Search knowledge base
        matches = search_knowledge_base(user_message, top_k=2)

        if matches and len(matches) > 0:
            top_match = matches[0]

            # Build response from best match
            response_text = top_match["answer"]

            # If multiple relevant matches, add a brief note about related topics
            related_topics = []
            if len(matches) > 1:
                related_topics = [m["topic"] for m in matches[1:]]

            # Generate next suggestions based on category
            suggestions = self._get_contextual_suggestions(top_match.get("category", ""), role)

            return {
                "answer": response_text,
                "sources": [
                    {"id": m["id"], "topic": m["topic"], "category": m["category"]}
                    for m in matches
                ],
                "related_topics": related_topics,
                "suggestions": suggestions,
                "intent_hint": top_match.get("category", "general"),
                "confidence": "high" if len(matches) >= 1 else "medium",
            }

        # No match — try role-specific fallback hints
        role_hint = self._get_role_specific_hint(message_lower, role)
        if role_hint:
            return {
                "answer": role_hint,
                "sources": [],
                "suggestions": QUICK_SUGGESTION_CHIPS[:4],
                "intent_hint": "role_hint",
                "confidence": "medium",
            }

        # Final fallback
        return {
            "answer": FALLBACK_RESPONSE,
            "sources": [],
            "suggestions": QUICK_SUGGESTION_CHIPS[:5],
            "intent_hint": "fallback",
            "confidence": "low",
        }

    def _is_greeting(self, text: str) -> bool:
        """Detect simple greetings."""
        greetings = ["hi", "hello", "hey", "good morning", "good afternoon", "good evening",
                     "namaste", "hii", "helo", "howdy", "sup", "what's up", "greetings"]
        return any(text.strip() == g or text.startswith(g + " ") or text.startswith(g + "!") for g in greetings)

    def _get_contextual_suggestions(self, category: str, role: Optional[str]) -> List[str]:
        """Return context-aware follow-up suggestion chips."""
        category_suggestions = {
            "school_policy": [
                "What is the attendance policy?",
                "Upcoming school holidays?",
                "School uniform rules?",
                "Fee payment deadlines?",
            ],
            "homework_tutor": [
                "Explain photosynthesis",
                "Newton's laws of motion",
                "How to write an essay?",
                "Quadratic equation formula?",
                "Parts of a cell?",
            ],
            "academics": [
                "Exam preparation tips?",
                "Explain photosynthesis",
                "Newton's laws of motion",
                "School timings?",
            ],
            "communication": [
                "How to contact teachers?",
                "School office hours?",
                "Upcoming parent-teacher conference?",
            ],
        }

        return category_suggestions.get(category, QUICK_SUGGESTION_CHIPS[:4])

    def _get_role_specific_hint(self, text: str, role: Optional[str]) -> Optional[str]:
        """Return a role-specific redirect for attendance/action queries that belong in the main assistant."""
        role = (role or "STUDENT").upper()

        attendance_keywords = ["attendance", "absent", "present", "mark"]
        if any(kw in text for kw in attendance_keywords):
            if role == "STUDENT":
                return (
                    "📊 For **your personal attendance**, please use the main assistant above and ask:\n"
                    "*\"What is my attendance?\"*\n\n"
                    "The Chatbot handles school knowledge and general queries. "
                    "The main assistant handles your live data (attendance, grades, teacher contact, etc.)"
                )
            elif role == "TEACHER":
                return (
                    "📝 To **mark or view class attendance**, use the main assistant above.\n"
                    "Try: *\"Show Class 10-A attendance roster\"* or *\"Mark Rahul present today\"*"
                )
            elif role == "PARENT":
                return (
                    "👨‍👩‍👧 To check **your child's attendance**, use the main assistant and ask:\n"
                    "*\"How is Rahul's attendance?\"*"
                )

        return None

    def get_knowledge_categories(self) -> List[str]:
        """Return all available topic categories in the knowledge base."""
        categories = list({entry["category"] for entry in KNOWLEDGE_BASE})
        return sorted(categories)

    def get_suggestions(self) -> List[str]:
        """Return default suggestion chips."""
        return QUICK_SUGGESTION_CHIPS


chatbot_service = ChatbotService()
