"""
Interactive quiz data for the floating chatbot widget.
5 topics × 3 MCQs each = 15 total questions.
Each question: text, 4 options, correct_index (0-based), explanation shown after answering.
"""

from typing import List, Dict, Any, Optional

QUIZ_TOPICS = {
    "photosynthesis": {
        "label": "Photosynthesis",
        "subject": "Science / Biology",
        "emoji": "🌿",
        "questions": [
            {
                "id": "PH-1",
                "question": "Which pigment in plant cells absorbs sunlight during photosynthesis?",
                "options": ["Melanin", "Chlorophyll", "Haemoglobin", "Carotene"],
                "correct_index": 1,
                "explanation": "**Chlorophyll** is the green pigment in chloroplasts. It absorbs red and blue light, reflecting green — that's why plants look green!"
            },
            {
                "id": "PH-2",
                "question": "What are the two main reactants of photosynthesis?",
                "options": [
                    "Oxygen and Glucose",
                    "Carbon Dioxide and Water",
                    "Nitrogen and Sunlight",
                    "Water and Oxygen"
                ],
                "correct_index": 1,
                "explanation": "Photosynthesis uses **CO₂** (from air) and **H₂O** (from soil), powered by sunlight, to produce glucose and oxygen.\n`6CO₂ + 6H₂O + Light → C₆H₁₂O₆ + 6O₂`"
            },
            {
                "id": "PH-3",
                "question": "Where inside the plant cell does photosynthesis take place?",
                "options": ["Mitochondria", "Nucleus", "Chloroplast", "Ribosome"],
                "correct_index": 2,
                "explanation": "Photosynthesis occurs in the **Chloroplast** — light reactions in the thylakoid and the Calvin Cycle in the stroma."
            }
        ]
    },
    "newton": {
        "label": "Newton's Laws",
        "subject": "Physics",
        "emoji": "⚡",
        "questions": [
            {
                "id": "NW-1",
                "question": "Newton's First Law says an object at rest stays at rest unless acted on by what?",
                "options": ["Gravity only", "An unbalanced external force", "Friction", "Air resistance"],
                "correct_index": 1,
                "explanation": "**Newton's First Law (Inertia)** — An object stays in its current state unless an **external unbalanced force** acts on it. Example: A book stays still until you push it!"
            },
            {
                "id": "NW-2",
                "question": "What is the formula for Newton's Second Law?",
                "options": ["F = mv", "F = ma", "F = m/a", "F = m²a"],
                "correct_index": 1,
                "explanation": "**F = ma** (Force = Mass × Acceleration)\n\nIf you push a 5 kg box with 10 N: Acceleration = 10/5 = **2 m/s²**"
            },
            {
                "id": "NW-3",
                "question": "A rocket moves forward because exhaust is pushed backward. Which law explains this?",
                "options": ["Newton's First Law", "Newton's Second Law", "Newton's Third Law", "Law of Gravitation"],
                "correct_index": 2,
                "explanation": "**Newton's Third Law** — 'For every action, there is an equal and opposite reaction.' Gas pushed back (action) → rocket pushed forward (reaction). 🚀"
            }
        ]
    },
    "quadratic": {
        "label": "Quadratic Equations",
        "subject": "Mathematics",
        "emoji": "📐",
        "questions": [
            {
                "id": "QD-1",
                "question": "What is the standard form of a quadratic equation?",
                "options": ["ax + b = 0", "ax² + bx + c = 0", "ax³ + bx² = 0", "a/x + b = 0"],
                "correct_index": 1,
                "explanation": "**Standard form: ax² + bx + c = 0** where:\n- `a` = coefficient of x² (cannot be 0)\n- `b` = coefficient of x\n- `c` = constant term"
            },
            {
                "id": "QD-2",
                "question": "Solve: x² - 5x + 6 = 0. What are the roots?",
                "options": ["x = 2, x = 3", "x = -2, x = -3", "x = 1, x = 6", "x = 5, x = 1"],
                "correct_index": 0,
                "explanation": "Using **x = (-b ± √(b²-4ac)) / 2a**:\n- Discriminant = 25 - 24 = 1\n- x = (5 ± 1) / 2\n- **x = 3** and **x = 2** ✓\n\nVerify: (x-2)(x-3) = x² - 5x + 6 ✓"
            },
            {
                "id": "QD-3",
                "question": "If the discriminant (b²-4ac) is negative, what does this mean?",
                "options": ["Two equal real roots", "Two distinct real roots", "No real roots (complex)", "One root is zero"],
                "correct_index": 2,
                "explanation": "When **b²-4ac < 0** → **No real roots** (complex/imaginary solutions).\n\nTip: Always check the discriminant first before solving!"
            }
        ]
    },
    "cell": {
        "label": "Cell Biology",
        "subject": "Biology",
        "emoji": "🔬",
        "questions": [
            {
                "id": "CB-1",
                "question": "Which organelle is called the 'powerhouse of the cell'?",
                "options": ["Nucleus", "Ribosome", "Mitochondria", "Vacuole"],
                "correct_index": 2,
                "explanation": "**Mitochondria** produces ATP (energy) through cellular respiration.\n\nMnemonic: **M**ighty **M**itochondria **M**akes **M**ore ATP 💪"
            },
            {
                "id": "CB-2",
                "question": "Which structure is found in plant cells but NOT in animal cells?",
                "options": ["Nucleus", "Cell Wall", "Mitochondria", "Cell Membrane"],
                "correct_index": 1,
                "explanation": "**Cell Wall** (made of cellulose) is unique to plant cells. It gives rigidity and structure. Animal cells only have a flexible cell membrane."
            },
            {
                "id": "CB-3",
                "question": "What is the control center of the cell that contains DNA?",
                "options": ["Cytoplasm", "Chloroplast", "Nucleus", "Endoplasmic Reticulum"],
                "correct_index": 2,
                "explanation": "The **Nucleus** is the control center — it houses the cell's DNA and directs all activities: growth, protein synthesis, and cell division."
            }
        ]
    },
    "essay": {
        "label": "Essay Writing",
        "subject": "English",
        "emoji": "✍️",
        "questions": [
            {
                "id": "EW-1",
                "question": "In a 5-paragraph essay, how many body paragraphs are there?",
                "options": ["1", "2", "3", "4"],
                "correct_index": 2,
                "explanation": "A 5-paragraph essay = 1 Introduction + **3 Body Paragraphs** + 1 Conclusion.\n\nEach body paragraph supports one main argument with evidence."
            },
            {
                "id": "EW-2",
                "question": "What is a 'thesis statement'?",
                "options": [
                    "The first sentence of any paragraph",
                    "A sentence stating the essay's main argument",
                    "The last sentence of the conclusion",
                    "A quote from a famous author"
                ],
                "correct_index": 1,
                "explanation": "A **thesis statement** (usually last sentence of the intro) clearly states your **main argument**.\n\nExample: *'Social media negatively affects teenagers' mental health.'*"
            },
            {
                "id": "EW-3",
                "question": "Which transition word best signals a contrasting point?",
                "options": ["Furthermore", "In addition", "However", "Similarly"],
                "correct_index": 2,
                "explanation": "**'However'** signals contrast or contradiction.\n\n- Addition: Furthermore, Moreover, In addition\n- Contrast: **However**, Nevertheless, On the other hand\n- Conclusion: Therefore, Thus, In conclusion"
            }
        ]
    },
    "chemistry": {
        "label": "Chemistry & Elements",
        "subject": "Science / Chemistry",
        "emoji": "🧪",
        "questions": [
            {
                "id": "CH-1",
                "question": "What is the atomic number of Carbon on the periodic table?",
                "options": ["4", "6", "8", "12"],
                "correct_index": 1,
                "explanation": "**Carbon has atomic number 6**, meaning it has 6 protons in its nucleus. It forms 4 covalent bonds, which is the foundation of organic chemistry!"
            },
            {
                "id": "CH-2",
                "question": "What is the pH value of pure water at room temperature (neutral)?",
                "options": ["0", "5", "7", "14"],
                "correct_index": 2,
                "explanation": "Pure water has a **pH of 7 (Neutral)**. Values below 7 are acidic (like lemon juice or HCl), while values above 7 are basic/alkaline (like soap or bleach)."
            },
            {
                "id": "CH-3",
                "question": "Which chemical bond involves the sharing of electron pairs between atoms?",
                "options": ["Ionic Bond", "Covalent Bond", "Metallic Bond", "Hydrogen Bond"],
                "correct_index": 1,
                "explanation": "A **Covalent Bond** forms when two non-metal atoms share electrons (e.g. H₂O, CO₂). Ionic bonds involve the complete transfer of electrons (e.g. NaCl)."
            }
        ]
    },
    "computerscience": {
        "label": "Computer Science & AI",
        "subject": "Technology / AI",
        "emoji": "💻",
        "questions": [
            {
                "id": "CS-1",
                "question": "Which data structure follows the First-In, First-Out (FIFO) principle?",
                "options": ["Stack", "Queue", "Tree", "Graph"],
                "correct_index": 1,
                "explanation": "A **Queue** follows **FIFO (First-In, First-Out)** — just like a ticket line! A Stack follows LIFO (Last-In, First-Out)."
            },
            {
                "id": "CS-2",
                "question": "In Python, which keyword is used to define a reusable function?",
                "options": ["func", "define", "def", "function"],
                "correct_index": 2,
                "explanation": "In Python, **def** is the keyword used to declare functions. Example: `def calculate_attendance(present, total): return (present/total)*100`"
            },
            {
                "id": "CS-3",
                "question": "What does Zero-Trust RBAC mean in cybersecurity?",
                "options": [
                    "Users can access anything without login",
                    "Role-Based Access Control where permissions are verified server-side on every request",
                    "Passwords are never stored",
                    "Only admins can use the app"
                ],
                "correct_index": 1,
                "explanation": "**Zero-Trust Role-Based Access Control (RBAC)** means 'never trust, always verify'. Every single API request validates user role and resource ownership on the server side!"
            }
        ]
    }
}

EXAM_CALENDAR = [
    {
        "name": "Term 1 Mid-Term Exams",
        "date": "2026-09-05",
        "subjects": ["Mathematics", "Science", "English", "Social Studies"],
        "type": "mid_term",
        "emoji": "📝"
    },
    {
        "name": "Term 1 Final Exams",
        "date": "2026-11-20",
        "subjects": ["All Subjects"],
        "type": "final",
        "emoji": "📋"
    },
    {
        "name": "Class 10 Board Exams",
        "date": "2027-02-15",
        "subjects": ["All Subjects"],
        "type": "board",
        "emoji": "🎓"
    }
]

STUDY_PLAN_WEEKS = [
    {"week": "Week 4 Before", "emoji": "📚", "focus": "Cover full syllabus — list all topics per subject"},
    {"week": "Week 3 Before", "emoji": "📝", "focus": "Detailed notes + solve textbook exercises"},
    {"week": "Week 2 Before", "emoji": "🔁", "focus": "Revision + previous year question papers"},
    {"week": "Week 1 Before", "emoji": "⚡", "focus": "Quick revision of formulas, diagrams, key terms only"},
    {"week": "Night Before",  "emoji": "😴", "focus": "Light review only — 8 hours sleep + eat well!"}
]


def get_quiz(topic: str) -> Optional[Dict]:
    """Return quiz data for a given topic slug (fuzzy match)."""
    topic_clean = topic.lower().strip()
    for key, data in QUIZ_TOPICS.items():
        if topic_clean in key or key in topic_clean:
            return {"topic": key, **data}
    return None


def list_quiz_topics() -> List[Dict]:
    """Return all available quiz topics."""
    return [
        {"slug": k, "label": v["label"], "subject": v["subject"], "emoji": v["emoji"]}
        for k, v in QUIZ_TOPICS.items()
    ]


def get_next_exam() -> Optional[Dict]:
    """Return the soonest upcoming exam based on today's date."""
    from datetime import date
    today = date.today()
    for exam in EXAM_CALENDAR:
        exam_date = date.fromisoformat(exam["date"])
        if exam_date >= today:
            delta = (exam_date - today).days
            return {**exam, "days_remaining": delta, "exam_date_str": exam_date.strftime("%d %B %Y")}
    return None
