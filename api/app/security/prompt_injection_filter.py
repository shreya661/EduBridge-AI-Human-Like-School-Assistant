"""Lightweight detection for obvious prompt-injection attempts.

Pattern matching is deliberately only a first-stage signal and is never used as an
authorization mechanism or a complete prompt-injection defense.
"""

import re

from pydantic import BaseModel, ConfigDict


_SUSPICIOUS_PATTERNS = {
    "ignore_previous_instructions": re.compile(r"ignore\s+(all\s+)?previous\s+instructions", re.I),
    "reveal_system_prompt": re.compile(r"(reveal|show)\s+(your\s+)?system\s+prompt", re.I),
    "request_api_key": re.compile(r"(show|reveal|give)\s+(me\s+)?(your\s+)?api\s*key", re.I),
    "bypass_authorization": re.compile(r"bypass\s+(the\s+)?authorization", re.I),
    "pretend_privileged_role": re.compile(r"pretend\s+(i\s+am|i'm)\s+(the\s+)?principal", re.I),
}


class PromptInjectionAssessment(BaseModel):
    """Detection result for telemetry or later policy handling."""

    model_config = ConfigDict(frozen=True)

    flagged: bool
    indicators: tuple[str, ...] = ()


def assess_prompt_injection(message: str) -> PromptInjectionAssessment:
    """Flag known obvious instruction-override patterns without changing permissions."""
    indicators = tuple(
        name for name, pattern in _SUSPICIOUS_PATTERNS.items() if pattern.search(message)
    )
    return PromptInjectionAssessment(flagged=bool(indicators), indicators=indicators)
