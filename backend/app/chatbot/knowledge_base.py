"""
School Knowledge Base — Curated Q&A dataset covering school policies,
academic topics, exam rules, fee structures, and general school help.
Supports keyword-based retrieval for the chatbot/tutor assistant.
"""

from typing import List, Dict, Optional

KNOWLEDGE_BASE: List[Dict] = [
    # ── SCHOOL GENERAL POLICIES ──────────────────────────────────────────────
    {
        "id": "KB-001",
        "topic": "School Timings",
        "category": "school_policy",
        "tags": ["timing", "time", "hours", "school", "open", "close"],
        "question": "What are the school timings?",
        "answer": (
            "📅 **School Timings — XYZ AI School**\n\n"
            "• **Morning Assembly**: 8:15 AM\n"
            "• **Classes Begin**: 8:30 AM (Period 1)\n"
            "• **Lunch Break**: 12:00 PM – 12:30 PM\n"
            "• **Classes End**: 2:00 PM (Period 6)\n"
            "• **Office Hours**: 8:00 AM – 4:00 PM (Monday–Friday)\n\n"
            "Late arrivals after 8:30 AM must sign in at the reception. Three late arrivals count as one absence."
        )
    },
    {
        "id": "KB-002",
        "topic": "Attendance Policy",
        "category": "school_policy",
        "tags": ["attendance", "policy", "minimum", "percentage", "75%", "requirement", "rules"],
        "question": "What is the minimum attendance requirement?",
        "answer": (
            "📋 **Attendance Policy**\n\n"
            "• **Minimum Required**: 75% attendance is compulsory for all students.\n"
            "• Students below 75% may be **barred from appearing in final exams** unless a medical exemption is granted.\n"
            "• **Medical leave** requires a doctor's certificate within 3 days of returning.\n"
            "• Parents are notified via WhatsApp/SMS when attendance drops below 80%.\n\n"
            "To check your current attendance, just ask: *\"What is my attendance?\"*"
        )
    },
    {
        "id": "KB-003",
        "topic": "Fee Structure",
        "category": "school_policy",
        "tags": ["fee", "fees", "tuition", "payment", "amount", "cost", "charges"],
        "question": "What is the fee structure?",
        "answer": (
            "💰 **Annual Fee Structure (2025–2026)**\n\n"
            "| Grade | Tuition Fee | Activity Fee | Total/Year |\n"
            "|-------|-------------|--------------|------------|\n"
            "| Class 9 | ₹42,000 | ₹8,000 | ₹50,000 |\n"
            "| Class 10 | ₹45,000 | ₹8,000 | ₹53,000 |\n"
            "| Class 11 | ₹52,000 | ₹10,000 | ₹62,000 |\n\n"
            "• **Payment Schedules**: Quarterly (April, July, October, January)\n"
            "• **Late Fee**: ₹200/month after the 10th of the payment month.\n"
            "• **Fee Waivers**: Available for meritorious students (75%+ in previous year). Contact the office."
        )
    },
    {
        "id": "KB-004",
        "topic": "Exam Schedule",
        "category": "academics",
        "tags": ["exam", "test", "exam date", "mid-term", "final", "schedule", "examination"],
        "question": "When are the upcoming examinations?",
        "answer": (
            "📝 **Upcoming Examination Schedule (2025–2026)**\n\n"
            "**Term 1 Mid-Term Exams:**\n"
            "• Date: **5–10 September 2026**\n"
            "• Subjects: Mathematics, Science, English, Social Studies\n"
            "• Venue: Hall A and Hall B\n\n"
            "**Term 1 Final Exams:**\n"
            "• Date: **November 20 – December 3, 2026**\n\n"
            "**Term 2 Final Board Exams (Class 10):**\n"
            "• Date: **February 15 – March 5, 2027** (Board-scheduled)\n\n"
            "💡 *Always confirm exact exam timetables on the School Calendar (click 📅 School Calendar in the sidebar).*"
        )
    },
    {
        "id": "KB-005",
        "topic": "School Uniform Rules",
        "category": "school_policy",
        "tags": ["uniform", "dress", "code", "clothes", "wear"],
        "question": "What is the school uniform and dress code?",
        "answer": (
            "👕 **Uniform & Dress Code Policy**\n\n"
            "**Boys (Classes 9–12):**\n"
            "• White full-sleeve shirt with school monogram\n"
            "• Dark grey trousers and black formal shoes\n"
            "• School tie and black belt\n\n"
            "**Girls (Classes 9–12):**\n"
            "• White full-sleeve shirt with school monogram\n"
            "• Dark grey skirt or trousers and black formal shoes\n"
            "• School tie (optional)\n\n"
            "• Casual / Non-Uniform Day: Last Saturday of each month 🎉\n"
            "• Uniform violations may result in a note sent home to parents."
        )
    },
    {
        "id": "KB-006",
        "topic": "School Holidays",
        "category": "school_policy",
        "tags": ["holiday", "holidays", "vacation", "break", "closed", "diwali", "holi", "ganesh"],
        "question": "What are the upcoming school holidays?",
        "answer": (
            "🌴 **Upcoming School Holidays (2025–2026 Academic Year)**\n\n"
            "| Date | Holiday | Duration |\n"
            "|------|---------|----------|\n"
            "| 15 Sep 2026 | Ganesh Chaturthi | 1 day |\n"
            "| 02 Oct 2026 | Gandhi Jayanti | 1 day |\n"
            "| 02–04 Nov 2026 | Diwali Vacation | 3 days |\n"
            "| 14 Jan 2027 | Makar Sankranti | 1 day |\n"
            "| 26 Jan 2027 | Republic Day | 1 day |\n"
            "| 14 Mar 2027 | Holi | 1 day |\n\n"
            "For the complete calendar, click **📅 School Calendar** in the sidebar."
        )
    },

    # ── ACADEMICS & HOMEWORK TUTOR ────────────────────────────────────────────
    {
        "id": "KB-007",
        "topic": "Mathematics — Quadratic Equations",
        "category": "homework_tutor",
        "tags": ["maths", "math", "quadratic", "equation", "formula", "algebra", "solve"],
        "question": "How do I solve a quadratic equation?",
        "answer": (
            "📐 **Solving Quadratic Equations**\n\n"
            "A **Quadratic Equation** is in the form: `ax² + bx + c = 0`\n\n"
            "**Method 1 — Quadratic Formula (Always works!):**\n"
            "```\nx = (-b ± √(b² - 4ac)) / 2a\n```\n"
            "**Step-by-Step Example:** Solve `2x² - 4x - 6 = 0`\n"
            "1. a = 2, b = -4, c = -6\n"
            "2. Discriminant: b² - 4ac = 16 + 48 = **64**\n"
            "3. x = (4 ± 8) / 4 → **x = 3** or **x = -1** ✓\n\n"
            "**Method 2 — Factorization:** Split the middle term and factor.\n"
            "**Method 3 — Completing the Square**: Useful in proofs and complex cases.\n\n"
            "💡 *Tip: If the discriminant (b² - 4ac) < 0, there are no real roots.*"
        )
    },
    {
        "id": "KB-008",
        "topic": "Science — Photosynthesis",
        "category": "homework_tutor",
        "tags": ["science", "biology", "photosynthesis", "plant", "leaves", "light", "chlorophyll"],
        "question": "Explain photosynthesis",
        "answer": (
            "🌿 **Photosynthesis — How Plants Make Food**\n\n"
            "Photosynthesis is the process by which green plants convert sunlight into food (glucose).\n\n"
            "**The Chemical Equation:**\n"
            "```\n6CO₂ + 6H₂O + Light Energy → C₆H₁₂O₆ + 6O₂\n```\n"
            "*(Carbon dioxide + Water + Sunlight → Glucose + Oxygen)*\n\n"
            "**Key Points:**\n"
            "• **Chlorophyll** (the green pigment in leaves) absorbs sunlight.\n"
            "• Takes place in the **chloroplasts** of plant cells.\n"
            "• **Light Reactions** (in thylakoid): Split water molecules, release oxygen as a byproduct.\n"
            "• **Dark Reactions / Calvin Cycle** (in stroma): Convert CO₂ into glucose using energy from light reactions.\n\n"
            "💡 *Photosynthesis is why forests are called the 'lungs of the Earth' — they produce oxygen for us to breathe!*"
        )
    },
    {
        "id": "KB-009",
        "topic": "English — Essay Writing Tips",
        "category": "homework_tutor",
        "tags": ["english", "essay", "writing", "structure", "paragraph", "composition", "tips"],
        "question": "How do I write a good essay?",
        "answer": (
            "✍️ **How to Write a Great Essay**\n\n"
            "**5-Paragraph Essay Structure:**\n\n"
            "1. **Introduction** (1 paragraph)\n"
            "   - Hook: Start with a striking fact, quote, or question.\n"
            "   - Background: Give brief context.\n"
            "   - Thesis Statement: Your main argument (1 clear sentence).\n\n"
            "2. **Body Paragraphs** (3 paragraphs)\n"
            "   - Start each with a **Topic Sentence**.\n"
            "   - Add 2–3 supporting **evidence/examples**.\n"
            "   - End with a **Linking Sentence** connecting to the next paragraph.\n\n"
            "3. **Conclusion** (1 paragraph)\n"
            "   - Restate your thesis (don't copy it!)\n"
            "   - Summarize your main points.\n"
            "   - End with a **call-to-action or final thought**.\n\n"
            "📝 *Quick Tips: Use varied sentence lengths. Avoid passive voice. Use transition words like 'Furthermore', 'In contrast', 'However'.*"
        )
    },
    {
        "id": "KB-010",
        "topic": "Science — Newton's Laws of Motion",
        "category": "homework_tutor",
        "tags": ["newton", "physics", "motion", "force", "acceleration", "laws", "inertia"],
        "question": "Explain Newton's laws of motion",
        "answer": (
            "⚡ **Newton's Three Laws of Motion**\n\n"
            "**Law 1 — Law of Inertia:**\n"
            "> 'An object at rest stays at rest, and an object in motion stays in motion unless acted upon by an external force.'\n"
            "• Example: You slide forward when a car brakes suddenly.\n\n"
            "**Law 2 — Law of Acceleration:**\n"
            "> 'Force = Mass × Acceleration' → **F = ma**\n"
            "• Example: A heavier ball needs more force to accelerate the same amount.\n\n"
            "**Law 3 — Law of Action & Reaction:**\n"
            "> 'For every action, there is an equal and opposite reaction.'\n"
            "• Example: A rocket pushes gas downward → the gas pushes the rocket upward! 🚀\n\n"
            "💡 *Remember: F = ma is your best friend in Physics numericals!*"
        )
    },
    {
        "id": "KB-011",
        "topic": "Admissions & Enrollment",
        "category": "school_policy",
        "tags": ["admission", "enroll", "join", "new student", "registration", "apply"],
        "question": "How does admission work?",
        "answer": (
            "🏫 **Admission & Enrollment Process**\n\n"
            "**New Student Admission Steps:**\n"
            "1. **Application Form**: Collect from the school office or download from the portal.\n"
            "2. **Entrance Assessment**: Written test in Math, Science, and English (for Grades 9–12).\n"
            "3. **Document Submission**:\n"
            "   - Previous year's mark sheet\n"
            "   - Transfer certificate (TC)\n"
            "   - Birth certificate\n"
            "   - 4 passport-size photographs\n"
            "   - Aadhar card (student + parent)\n"
            "4. **Confirmation & Fee Payment**: Seat is confirmed upon fee payment.\n\n"
            "📅 **Admission Season**: April–June (for the next academic year)\n"
            "📞 Contact the school office at the front desk for exact dates and entrance test schedules."
        )
    },
    {
        "id": "KB-012",
        "topic": "How to Contact a Teacher",
        "category": "communication",
        "tags": ["contact", "teacher", "message", "reach", "talk", "meeting", "appointment"],
        "question": "How do I contact my teacher?",
        "answer": (
            "📬 **How to Contact a Teacher**\n\n"
            "You have 3 easy ways to reach your teacher through XYZ AI:\n\n"
            "1. **AI Assistant Request** (Fastest!)\n"
            "   Type: *\"I want to talk to my class teacher\"*\n"
            "   → The AI will create a consultation ticket and notify the teacher.\n\n"
            "2. **Escalation System** 🔴\n"
            "   Click the red **Escalate to Human** button at the bottom of the chat.\n"
            "   Select 'Teacher' and state your reason — the school will arrange a callback.\n\n"
            "3. **Direct School Office**\n"
            "   Visit the school reception during office hours (8:00 AM – 4:00 PM) and request a teacher meeting slip.\n\n"
            "*Note: Teacher contact is role-restricted for security. Parents and Students can both request teacher consultations.*"
        )
    },
    {
        "id": "KB-013",
        "topic": "Library Rules",
        "category": "school_policy",
        "tags": ["library", "book", "borrow", "return", "reading", "fine", "lending"],
        "question": "What are the school library rules?",
        "answer": (
            "📚 **School Library Rules & Borrowing Policy**\n\n"
            "• **Library Hours**: 8:30 AM – 3:00 PM (Mon–Sat)\n"
            "• **Borrowing Limit**: 2 books at a time per student\n"
            "• **Loan Period**: 14 days — renewable once if no waiting list\n"
            "• **Late Return Fine**: ₹2 per day per book\n"
            "• **Silence Zone**: No phone calls or conversations in the reading area\n"
            "• **Lost Book**: Must be replaced or pay the current market price\n\n"
            "💡 *Ask the librarian for reference books on Math, Science, or Hindi for exam preparation — they're available for in-library reading only.*"
        )
    },
    {
        "id": "KB-014",
        "topic": "Science — Cell Biology",
        "category": "homework_tutor",
        "tags": ["cell", "biology", "nucleus", "organelle", "membrane", "mitochondria", "science"],
        "question": "What are the parts of a cell?",
        "answer": (
            "🔬 **Parts of a Cell (Class 9–10 Biology)**\n\n"
            "**Animal Cell vs Plant Cell:**\n\n"
            "| Organelle | Function | Animal | Plant |\n"
            "|-----------|----------|--------|-------|\n"
            "| **Cell Membrane** | Controls what enters/exits | ✓ | ✓ |\n"
            "| **Cell Wall** | Provides rigid structure | ✗ | ✓ |\n"
            "| **Nucleus** | Control centre (DNA storage) | ✓ | ✓ |\n"
            "| **Mitochondria** | 'Powerhouse' — produces ATP energy | ✓ | ✓ |\n"
            "| **Chloroplast** | Photosynthesis (uses sunlight) | ✗ | ✓ |\n"
            "| **Vacuole** | Storage — large in plants, small in animals | Small | Large |\n"
            "| **Endoplasmic Reticulum** | Protein/lipid transport | ✓ | ✓ |\n\n"
            "💡 *Mnemonic for Mitochondria: 'Mighty Mitochondria Makes More ATP!'*"
        )
    },
    {
        "id": "KB-015",
        "topic": "Exam Preparation Tips",
        "category": "homework_tutor",
        "tags": ["study", "tips", "preparation", "exams", "how to study", "revision", "prepare"],
        "question": "How do I prepare for exams?",
        "answer": (
            "🎯 **Smart Exam Preparation Strategy**\n\n"
            "**4-Week Study Plan (Before Exams):**\n\n"
            "📌 **Week 4–3 Before**: Cover all syllabus topics. Mark difficult ones.\n"
            "📌 **Week 2 Before**: Revise notes + solve previous year question papers.\n"
            "📌 **Week 1 Before**: Quick revision of key formulas, definitions, and diagrams. Avoid new topics!\n"
            "📌 **Night Before**: Light review only. Sleep 8 hours. Eat well! 🍎\n\n"
            "**Power Study Tips:**\n"
            "• Use the **Pomodoro Technique**: 25 mins study → 5 min break → repeat\n"
            "• Practice diagrams and derivations with your hand (not just reading)\n"
            "• Teach the concept to someone else — best way to know if you've understood!\n"
            "• Stay hydrated and take short walks between study sessions 🚶\n\n"
            "💡 *You've got this! Consistent small efforts beat last-minute cramming every time.*"
        )
    },
]


def search_knowledge_base(query: str, top_k: int = 3) -> List[Dict]:
    """
    Keyword-based search over the knowledge base.
    Returns the top matching knowledge entries for a given query string.
    """
    query_lower = query.lower().strip()

    scored: List[tuple] = []

    for entry in KNOWLEDGE_BASE:
        score = 0

        # Check tags (highest weight)
        for tag in entry.get("tags", []):
            if tag.lower() in query_lower:
                score += 3

        # Check question match
        question_words = entry["question"].lower().split()
        for word in question_words:
            if len(word) > 3 and word in query_lower:
                score += 2

        # Check topic words
        for word in entry["topic"].lower().split():
            if len(word) > 3 and word in query_lower:
                score += 2

        # Check category
        if entry.get("category", "") in query_lower:
            score += 1

        if score > 0:
            scored.append((score, entry))

    # Sort by score descending
    scored.sort(key=lambda x: x[0], reverse=True)

    return [entry for _, entry in scored[:top_k]]


def get_knowledge_entry_by_id(entry_id: str) -> Optional[Dict]:
    """Get a specific knowledge entry by its ID."""
    for entry in KNOWLEDGE_BASE:
        if entry["id"] == entry_id:
            return entry
    return None
