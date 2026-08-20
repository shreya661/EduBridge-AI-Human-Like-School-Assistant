"""Deterministic regex & keyword-based NLU classifier."""

import re
from typing import Optional, Tuple
from app.nlu.models import IntentType
from app.nlu.intents import Intent
from app.nlu.schemas import NLUResult, NLUEntities


class NLUClassifier:
    def __init__(self):
        self.intent_patterns = {
            Intent.VIEW_OWN_ATTENDANCE: [
                r"what.*my.*attendance",
                r"how.*much.*attendance.*me",
                r"my.*attendance",
                r"attendance.*mine",
                r"what is my attendance",
            ],
            Intent.VIEW_CHILD_ATTENDANCE: [
                r"child.*attendance",
                r"attendance.*child",
                r"how.*much.*attendance.*child",
                r"attendance.*kid",
                r"kid.*attendance",
                r"my child.*attendance",
                r"attendance for.*",
            ],
            Intent.MARK_ATTENDANCE: [
                r"mark.*absent",
                r"mark.*present",
                r"mark.*late",
                r"absent.*",
                r"present.*",
                r"mark.*attendance",
            ],
            Intent.VIEW_CLASS_ATTENDANCE: [
                r"class.*attendance",
                r"class.*roster",
                r"students.*class",
                r"class.*list",
                r"who.*class",
            ],
            Intent.VIEW_SCHOOL_ATTENDANCE: [
                r"overall.*attendance",
                r"total.*attendance",
                r"school.*attendance",
                r"all.*attendance",
            ],
            Intent.VIEW_SCHOOL_ANALYTICS: [
                r"analytics",
                r"report",
                r"attendance analytics",
                r"low attendance",
                r"flagged",
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
            Intent.UNSUPPORTED_REQUEST: [
                r"\bdelete\b",
                r"\bremove\b",
                r"\bdrop\b",
                r"hack\b",
                r"system prompt",
                r"api key",
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
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    return intent
        return Intent.UNSUPPORTED_REQUEST
    
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
        
        for status in ['present', 'absent', 'late', 'excused']:
            if re.search(rf"\b{status}\b", text.lower()):
                entities.attendance_status = status.upper()
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
