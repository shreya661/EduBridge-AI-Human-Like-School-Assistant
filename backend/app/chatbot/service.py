"""
Chatbot service — handles knowledge base lookup, quiz retrieval,
exam countdown calculations, live chat initiation, and context-aware replies.
"""

from typing import List, Dict, Optional, Any
from datetime import datetime

from app.chatbot.knowledge_base import (
    search_knowledge_base,
    KNOWLEDGE_BASE,
)
from app.chatbot.quiz_data import (
    get_quiz,
    get_next_exam,
    STUDY_PLAN_WEEKS,
    QUIZ_TOPICS,
)
from app.session.models import Role


GREETING_RESPONSES = [
    "👋 Hi there! I'm your **XYZ AI Tutor**. Ask me anything — attendance, exam schedules, homework help, school policies, or take a quick quiz!",
    "😊 Hello! Ready to learn! You can ask me about school timings, fee structure, exam dates, Newton's laws, photosynthesis, or live teacher support.",
    "🎓 Hey! I'm XYZ AI. How can I help you today? Try asking about attendance rules, holidays, quadratic formulas, or click **Quiz** below!",
]

FALLBACK_RESPONSE = (
    "🤔 I couldn't find an exact match in my knowledge base yet.\n\n"
    "Here are some things I **can** help you with:\n"
    "• 📋 School policies (timings, attendance rules, uniform, library)\n"
    "• 📝 Exam countdown, schedules, and study preparation tips\n"
    "• 🎯 Interactive mini-quizzes (Science, Physics, Math, Biology, English)\n"
    "• 💰 Fee structure and payment details\n"
    "• 🌿 Homework concepts (photosynthesis, Newton's laws, quadratic equations)\n"
    "• 👥 Live teacher contact & communication\n\n"
    "Try one of the suggestion chips or switch categories above!"
)

MODE_CHIPS = {
    "all": [
        "School timings?",
        "Upcoming holidays?",
        "Attendance policy?",
        "Explain photosynthesis",
        "Newton's laws of motion",
        "How to write an essay?",
        "Fee structure?",
        "Exam countdown?",
        "Quiz: Photosynthesis",
    ],
    "operations": [
        "What is my attendance?",
        "Mark Rahul present today",
        "Show Class 10-A roster",
        "Request teacher consultation",
        "View attendance analytics",
    ],
    "tutor": [
        "Explain photosynthesis",
        "Newton's laws of motion",
        "How do I solve a quadratic equation?",
        "What are the parts of a cell?",
        "How to write an essay?",
        "Exam preparation tips?",
    ],
    "faq": [
        "What are the school timings?",
        "Upcoming school holidays?",
        "What is the fee structure?",
        "School uniform rules?",
        "Library borrowing rules?",
        "How does admission work?",
    ],
    "quiz": [
        "Quiz: Photosynthesis",
        "Quiz: Newton's Laws",
        "Quiz: Quadratic Equations",
        "Quiz: Cell Biology",
        "Quiz: Essay Writing",
    ]
}


class ChatbotService:
    """Floating chatbot widget service — Knowledge base, Quiz, Countdown, Live chat."""

    def process_message(
        self,
        user_message: str,
        role: Optional[str] = "STUDENT",
        conversation_history: Optional[List[Dict]] = None,
    ) -> Dict[str, Any]:
        """
        Process an incoming user message and return structured chatbot payload.
        """
        msg = user_message.lower().strip()

        # 1. Check for Quiz request
        if "quiz" in msg or "test me" in msg or "practice test" in msg:
            for slug in ["photosynthesis", "newton", "quadratic", "cell", "essay"]:
                if slug in msg or ("math" in msg and slug == "quadratic") or ("physics" in msg and slug == "newton") or ("biology" in msg and slug == "cell") or ("science" in msg and slug == "photosynthesis") or ("english" in msg and slug == "essay"):
                    quiz_obj = get_quiz(slug)
                    if quiz_obj:
                        return {
                            "answer": f"🎯 **Mini-Quiz: {quiz_obj['label']}** ({quiz_obj['subject']})\nTest your understanding with 3 quick questions below! Select the correct option:",
                            "sources": [],
                            "suggestions": [f"Quiz: {t['label']}" for t in QUIZ_TOPICS.values() if t['label'] != quiz_obj['label']][:4],
                            "intent_hint": "quiz",
                            "quiz_data": quiz_obj,
                            "confidence": "high",
                        }
            # Default to Photosynthesis quiz if unspecified
            quiz_obj = get_quiz("photosynthesis")
            return {
                "answer": "🎯 Here is a quick **Science Mini-Quiz on Photosynthesis**! Choose your answer for each question below:",
                "sources": [],
                "suggestions": [f"Quiz: {t['label']}" for t in QUIZ_TOPICS.values()][:4],
                "intent_hint": "quiz",
                "quiz_data": quiz_obj,
                "confidence": "high",
            }

        # 2. Check for Exam Countdown / Study Plan
        if any(k in msg for k in ["exam countdown", "days to exam", "days left for exam", "study plan", "when is exam", "when are exams"]):
            next_exam = get_next_exam()
            if next_exam:
                return {
                    "answer": (
                        f"📅 **Upcoming Exam Milestone: {next_exam['name']}**\n\n"
                        f"⏳ **{next_exam['days_remaining']} Days Remaining** until {next_exam['exam_date_str']}.\n"
                        f"📚 Subjects: {', '.join(next_exam['subjects'])}\n\n"
                        f"**Recommended 4-Week Study Checklist:**"
                    ),
                    "sources": [],
                    "suggestions": ["Exam preparation tips?", "Quiz: Photosynthesis", "Quiz: Quadratic Equations", "School timings?"],
                    "intent_hint": "countdown",
                    "countdown_data": {
                        "exam": next_exam,
                        "study_plan": STUDY_PLAN_WEEKS
                    },
                    "confidence": "high",
                }

        # 3. Check for Live Teacher Chat request
        if any(k in msg for k in ["contact teacher", "talk to teacher", "reach teacher", "connect teacher", "human chat", "live chat"]):
            return {
                "answer": (
                    "👨‍🏫 **Connecting you to Live Teacher Support...**\n\n"
                    "I am opening a direct live messaging channel with your class teacher **Ms. Priya Sharma**.\n"
                    "Please wait a moment while the connection is established..."
                ),
                "sources": [],
                "suggestions": ["Cancel Live Chat", "What is the attendance policy?", "Exam countdown?"],
                "intent_hint": "live_chat_request",
                "confidence": "high",
            }

        # 4. Handle greetings
        if self._is_greeting(msg):
            import random
            greeting = random.choice(GREETING_RESPONSES)
            return {
                "answer": greeting,
                "sources": [],
                "suggestions": MODE_CHIPS["all"][:5],
                "intent_hint": "greeting",
                "confidence": "high",
            }

        # 5. Search knowledge base
        matches = search_knowledge_base(user_message, top_k=2)

        if matches and len(matches) > 0:
            top_match = matches[0]
            response_text = top_match["answer"]
            related_topics = [m["topic"] for m in matches[1:]] if len(matches) > 1 else []
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

        # 6. Operations redirect hint for live data
        role_hint = self._get_role_specific_hint(msg, role)
        if role_hint:
            return {
                "answer": role_hint,
                "sources": [],
                "suggestions": MODE_CHIPS["operations"][:4],
                "intent_hint": "operations_redirect",
                "confidence": "medium",
            }

        # 7. Fallback
        return {
            "answer": FALLBACK_RESPONSE,
            "sources": [],
            "suggestions": MODE_CHIPS["all"][:5],
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
                "Fee structure?",
            ],
            "homework_tutor": [
                "Quiz: Photosynthesis",
                "Explain photosynthesis",
                "Newton's laws of motion",
                "How to write an essay?",
                "Solve quadratic equation?",
            ],
            "academics": [
                "Exam countdown?",
                "Exam preparation tips?",
                "Quiz: Newton's Laws",
                "School timings?",
            ],
            "communication": [
                "Contact a teacher?",
                "School office hours?",
                "Upcoming parent-teacher conference?",
            ],
        }
        return category_suggestions.get(category, MODE_CHIPS["all"][:4])

    def _get_role_specific_hint(self, text: str, role: Optional[str]) -> Optional[str]:
        """Return a role-specific redirect for attendance/action queries that belong in the main assistant."""
        role = (role or "STUDENT").upper()
        attendance_keywords = ["attendance", "absent", "present", "roster", "mark "]
        if any(kw in text for kw in attendance_keywords):
            if role == "STUDENT":
                return (
                    "📊 For **your live verified attendance**, please use the main assistant above and ask:\n"
                    "*\"What is my attendance?\"*\n\n"
                    "The Chatbot handles tutoring & knowledge. The main assistant enforces your live Zero-Trust RBAC clearance!"
                )
            elif role == "TEACHER":
                return (
                    "📝 To **mark or view live class attendance**, use the main assistant above.\n"
                    "Try: *\"Show Class 10-A attendance roster\"* or *\"Mark Rahul present today\"*"
                )
            elif role == "PARENT":
                return (
                    "👨‍👩‍👧 To check **your child's live attendance**, use the main assistant and ask:\n"
                    "*\"How is Rahul's attendance?\"*"
                )
        return None

    def get_mode_chips(self, mode: str = "all") -> List[str]:
        """Return chips for a specific mode."""
        return MODE_CHIPS.get(mode.lower(), MODE_CHIPS["all"])

    def get_knowledge_categories(self) -> List[str]:
        """Return all available topic categories in the knowledge base."""
        categories = list({entry["category"] for entry in KNOWLEDGE_BASE})
        return sorted(categories)


chatbot_service = ChatbotService()
