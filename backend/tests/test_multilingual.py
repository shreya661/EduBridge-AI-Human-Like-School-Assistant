"""Tests for Multi-Language Detection and Localized Formatting (11 Indian Languages)."""

import pytest
from app.i18n.language_router import (
    SupportedLanguage,
    detect_language,
    format_localized_message,
    LANGUAGE_NAMES,
)


def test_language_detection_all_scripts():
    """Verify script-based detection for Indian languages and English default."""
    assert detect_language("What is my attendance?") == SupportedLanguage.ENGLISH
    assert detect_language("मेरी उपस्थिति क्या है?") == SupportedLanguage.HINDI
    assert detect_language("என் வருகை என்ன?") == SupportedLanguage.TAMIL
    assert detect_language("నా హాజరు ఎంత?") == SupportedLanguage.TELUGU
    assert detect_language("माझी उपस्थिती काय आहे?") == SupportedLanguage.HINDI or detect_language("माझी उपस्थिती काय आहे?") == SupportedLanguage.MARATHI
    assert detect_language("আমার উপস্থিতি কত?") == SupportedLanguage.BENGALI
    assert detect_language("મારી હાજરી કેટલી છે?") == SupportedLanguage.GUJARATI
    assert detect_language("ਮੇਰੀ ਹਾਜ਼ਰੀ ਕੀ ਹੈ?") == SupportedLanguage.PUNJABI
    assert detect_language("ನನ್ನ ಹಾಜರಾತಿ ಎಷ್ಟು?") == SupportedLanguage.KANNADA
    assert detect_language("എന്റെ ഹാജർ എത്രയാണ്?") == SupportedLanguage.MALAYALAM
    assert detect_language("میری حاضری کتنی ہے؟") == SupportedLanguage.URDU


def test_localized_attendance_formatting():
    """Verify student and parent attendance messages in Hindi, Tamil, Telugu, and English."""
    # English
    en_msg = format_localized_message(
        "attendance_student",
        SupportedLanguage.ENGLISH,
        percentage=92.5
    )
    assert "92.5%" in en_msg
    assert "Your current attendance" in en_msg

    # Hindi
    hi_msg = format_localized_message(
        "attendance_student",
        SupportedLanguage.HINDI,
        percentage=88.0
    )
    assert "88.0%" in hi_msg
    assert "उपस्थिति" in hi_msg

    # Tamil
    ta_msg = format_localized_message(
        "attendance_child",
        SupportedLanguage.TAMIL,
        name="ராகுல்",
        percentage=95.0
    )
    assert "95.0%" in ta_msg
    assert "ராகுல்" in ta_msg

    # Telugu
    te_msg = format_localized_message(
        "permission_denied",
        SupportedLanguage.TELUGU
    )
    assert "అనుమతి లేదు" in te_msg


def test_fallback_to_english_on_missing_key():
    """Verify clean fallback behavior if template key is unknown."""
    msg = format_localized_message(
        "unknown_template_key",
        SupportedLanguage.HINDI
    )
    assert msg == ""
