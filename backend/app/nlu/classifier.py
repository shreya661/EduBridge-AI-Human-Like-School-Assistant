"""Deterministic regex & keyword-based NLU classifier."""

import re
from typing import Optional, Tuple
from app.nlu.models import IntentType
from app.nlu.intents import Intent
from app.nlu.schemas import NLUResult, NLUEntities

INDIC_NAME_MAP = {
    # Gujarati
    "રાહુલ": "Rahul",
    "અર્જુન": "Arjun",
    "અનન્યા": "Ananya",
    "પ્રિયા": "Priya",
    "આરવ": "Aarav",
    "દિયા": "Diya",
    # Hindi / Devanagari
    "राहुल": "Rahul",
    "अर्जुन": "Arjun",
    "अनन्या": "Ananya",
    "प्रिया": "Priya",
    "आरव": "Aarav",
    "दिया": "Diya",
    # Tamil
    "ராகுல்": "Rahul",
    "அர்ஜுன்": "Arjun",
    "பிரியா": "Priya",
    # Telugu
    "రాహుల్": "Rahul",
    "అర్జున్": "Arjun",
    "ప్రియ": "Priya",
}


class NLUClassifier:
    def __init__(self):
        self.intent_patterns = {
            Intent.VIEW_OWN_ATTENDANCE: [
                r"what.*my.*attendance",
                r"how.*much.*attendance.*me",
                r"my.*attendance",
                r"attendance.*mine",
                r"what is my attendance",
                r"મારી.*હાજરી",
                r"હાજરી",
                r"मेरी.*उपस्थिति",
                r"मेरी.*हाजिरी",
                r"उपस्थिति",
                r"हाजिरी",
                r"என்.*வருகை",
                r"வருகை",
                r"నా.*హాజరు",
                r"హాజరు",
                r"माझी.*उपस्थिती",
                r"माझी.*हजेरी",
                r"আমার.*উপস্থিতি",
            ],
            Intent.VIEW_CHILD_ATTENDANCE: [
                r"child.*attendance",
                r"attendance.*child",
                r"how.*much.*attendance.*child",
                r"how is .* attendance",
                r".*'s attendance",
                r"how is .*",
                r"attendance.*for.*",
                r"attendance.*kid",
                r"kid.*attendance",
                r"my child.*attendance",
                r"attendance for.*",
                r"બાળક.*હાજરી",
                r"બાળકની.*હાજરી",
                r"દીકરા.*હાજરી",
                r"દીકરી.*હાજરી",
                r"बच्चे.*उपस्थिति",
                r"बच्चे.*हाजिरी",
                r"குழந்தை.*வருகை",
                r"పిల్లల.*హాజరు",
                r"मुलाची.*हजेरी",
            ],
            Intent.MARK_ATTENDANCE: [
                r"mark.*absent",
                r"mark.*present",
                r"mark.*late",
                r"\babsent\b",
                r"\bpresent\b",
                r"mark.*attendance",
                r"ગેરહાજર",
                r"હાજર",
                r"अनुपस्थित",
                r"उपस्थित",
                r"வராதவர்",
                r"வந்தவர்",
                r"గైర్హాజరు",
                r"హాజరు",
                r"गैरहजर",
                r"हजर",
            ],
            Intent.VIEW_CLASS_ATTENDANCE: [
                r"class.*attendance",
                r"class.*roster",
                r"students.*class",
                r"class.*list",
                r"who.*class",
                r"વર્ગ.*હાજરી",
                r"કક્ષા.*હાજરી",
                r"कक्षा.*उपस्थिति",
                r"வகுப்பு.*வருகை",
                r"తరగతి.*హాజరు",
            ],
            Intent.VIEW_SCHOOL_ATTENDANCE: [
                r"overall.*attendance",
                r"total.*attendance",
                r"school.*attendance",
                r"all.*attendance",
                r"કુલ.*હાજરી",
                r"શાળા.*હાજરી",
                r"कुल.*उपस्थिति",
                r"மொத்த.*வருகை",
                r"మొత్తం.*హాజరు",
            ],
            Intent.VIEW_SCHOOL_ANALYTICS: [
                r"analytics",
                r"report",
                r"attendance analytics",
                r"low attendance",
                r"flagged",
                r"અહેવાલ",
                r"વિશ્લેષણ",
                r"रिपोर्ट",
            ],
            Intent.ESCALATE_TO_TEACHER: [
                r"talk.*teacher",
                r"connect.*teacher",
                r"contact.*teacher",
                r"call.*teacher",
                r"speak.*teacher",
                r"teacher.*call",
                r"discuss.*teacher",
                r"escalate.*teacher",
                r"શિક્ષક",
                r"શિક્ષક.*સાથે.*વાત",
                r"અધ્યાપક",
                r"शिक्षक",
                r"अध्यापक",
                r"ஆசிரியர்",
                r"ఉపాధ్యాయుడు",
            ],
            Intent.ESCALATE_TO_MANAGEMENT: [
                r"talk.*principal",
                r"talk.*management",
                r"connect.*principal",
                r"contact.*management",
                r"contact.*principal",
                r"call.*management",
                r"speak.*management",
                r"admin.*callback",
                r"escalate.*management",
                r"પ્રિન્સિપાલ",
                r"મેનેજમેન્ટ",
                r"प्रिंसिपल",
                r"प्रबंधन",
            ],
            Intent.GREETING: [
                r"\bhello\b",
                r"\bhi\b",
                r"\bhey\b",
                r"\bgreetings\b",
                r"good morning",
                r"good afternoon",
                r"good evening",
                r"नमस्ते",
                r"வணக்கம்",
                r"నమస్కారం",
                r"नमस्कार",
                r"নমস্কার",
                r"નમસ્તે",
                r"ਸਤਿ ਸ੍ਰੀ ਅਕਾਲ",
                r"ನಮಸ್ಕಾರ",
                r"നമസ്കാരം",
                r"آداب",
            ],
            Intent.GENERAL_SCHOOL_QUERY: [
                r"schedule",
                r"timetable",
                r"time.?table",
                r"tomorrow.*class",
                r"class.*tomorrow",
                r"what.*class",
                r"holiday",
                r"calendar",
                r"school.*calendar",
                r"upcoming.*event",
                r"exam.*date",
                r"exam.*schedule",
                r"fee",
                r"homework",
                r"assignment",
                r"syllabus",
                r"role.*guide",
                r"what can i do",
                r"what.*permission",
                r"my.*name",
                r"who am i",
                r"my.*id",
                r"my.*class",
                r"my.*section",
                r"my.*grade",
                r"teacher.*name",
                r"school.*name",
                r"school.*timing",
                r"what.*time",
                r"help",
                r"what can you do",
                r"what.*support",
                r"analytics.*overview",
                r"school.*overview",
                r"show.*calendar",
                r"show.*guide",
                r"સમય.?પત્રક",
                r"ટાઈમ.?ટેબલ",
                r"समय.?सारणी",
                r"வகுப்பு.*அட்டவணை",
                r"时间表",
            ],
            Intent.UNSUPPORTED_REQUEST: [
                r"\bdelete\b",
                r"\bremove\b",
                r"\bdrop\b",
                r"hack\b",
                r"system prompt",
                r"api key",
                r"ignore.*instruction",
                r"jailbreak",
            ]
        }

    def classify(self, text: str) -> NLUResult:
        """Classify natural language text into intent and entities."""
        text_lower = text.lower().strip()
        
        detected_intent = self._detect_intent(text_lower)
        entities = self._extract_entities(text)
        requires_clarification, _ = self._check_clarification_needed(detected_intent, entities)
        
        return NLUResult(
            intent=detected_intent,
            entities=entities,
            confidence=1.0,
            requires_clarification=requires_clarification
        )
    
    def _detect_intent(self, text: str) -> Intent:
        # Try all explicit patterns first (GENERAL_SCHOOL_QUERY checked last before fallback)
        for intent, patterns in self.intent_patterns.items():
            if intent == Intent.GENERAL_SCHOOL_QUERY:
                continue  # check this after all specific intents
            for pattern in patterns:
                if re.search(pattern, text):
                    return intent
        # Try general school query patterns
        for pattern in self.intent_patterns.get(Intent.GENERAL_SCHOOL_QUERY, []):
            if re.search(pattern, text):
                return Intent.GENERAL_SCHOOL_QUERY
        # Default: treat as general school query rather than hard UNSUPPORTED
        return Intent.GENERAL_SCHOOL_QUERY
    
    def _extract_entities(self, text: str) -> NLUEntities:
        entities = NLUEntities()
        
        # Stop words to ignore during name extraction
        stop_words = {
            'the', 'and', 'for', 'with', 'from', 'to', 'what', 'how', 'is', 'my', 
            'today', 'yesterday', 'tomorrow', 'mark', 'delete', 'hello', 'hi', 
            'child', 'kid', 'student', 'attendance', 'absent', 'present', 'late', 'excused'
        }
        
        # Extract capitalized name tokens
        words = re.findall(r"\b[A-Z][a-z]+\b", text)
        candidate_words = [w for w in words if w.lower() not in stop_words]
        if candidate_words:
            entities.student_name = " ".join(candidate_words[:2])
        else:
            for indic_name, eng_name in INDIC_NAME_MAP.items():
                if indic_name in text:
                    entities.student_name = eng_name
                    break
        
        # Status extraction across languages
        status_map = {
            'ABSENT': ['absent', 'ગેરહાજર', 'अनुपस्थित', 'गैरहजर', 'வராதவர்', 'గైర్హాజరు', 'অনুপস্থিত'],
            'PRESENT': ['present', 'હાજર', 'उपस्थित', 'हजर', 'வந்தவர்', 'హాజరు', 'উপস্থিত'],
            'LATE': ['late', 'મોડું', 'વિલંબ', 'देरी', 'उशीर', 'தாமதம்', 'ఆలస్యం'],
            'EXCUSED': ['excused', 'રજા', 'छुट्टी', 'સૂચના', 'விடுமுறை']
        }
        for status_val, keywords in status_map.items():
            if any(kw in text.lower() for kw in keywords):
                entities.attendance_status = status_val
                break
        
        for date_expr in ['today', 'yesterday', 'tomorrow', 'now', 'current']:
            if re.search(rf"\b{date_expr}\b", text.lower()):
                entities.date = date_expr
                break
        
        class_matches = re.findall(r"\b\d{1,2}-[A-Z]\b", text)
        if class_matches:
            entities.class_name = class_matches[0]
        
        return entities
    
    def _check_clarification_needed(self, intent: Intent, entities: NLUEntities) -> Tuple[bool, Optional[str]]:
        if intent == Intent.VIEW_CHILD_ATTENDANCE:
            if not entities.student_name:
                return True, "Which child would you like me to check?"
        elif intent == Intent.MARK_ATTENDANCE:
            if not entities.student_name:
                return True, "Which student would you like to mark?"
        return False, None
