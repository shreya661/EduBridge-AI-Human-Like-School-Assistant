"""Multi-language detection and localized response formatting for 11 Indian languages."""

from enum import Enum
from typing import Dict, Any, Optional
import re


class SupportedLanguage(str, Enum):
    ENGLISH = "en"
    HINDI = "hi"
    TAMIL = "ta"
    TELUGU = "te"
    MARATHI = "mr"
    BENGALI = "bn"
    GUJARATI = "gu"
    PUNJABI = "pa"
    KANNADA = "kn"
    MALAYALAM = "ml"
    URDU = "ur"


LANGUAGE_NAMES: Dict[SupportedLanguage, str] = {
    SupportedLanguage.ENGLISH: "English",
    SupportedLanguage.HINDI: "Hindi (हिंदी)",
    SupportedLanguage.TAMIL: "Tamil (தமிழ்)",
    SupportedLanguage.TELUGU: "Telugu (తెలుగు)",
    SupportedLanguage.MARATHI: "Marathi (मराठी)",
    SupportedLanguage.BENGALI: "Bengali (বাংলা)",
    SupportedLanguage.GUJARATI: "Gujarati (ગુજરાતી)",
    SupportedLanguage.PUNJABI: "Punjabi (ਪੰਜਾਬੀ)",
    SupportedLanguage.KANNADA: "Kannada (ಕನ್ನಡ)",
    SupportedLanguage.MALAYALAM: "Malayalam (മലയാളം)",
    SupportedLanguage.URDU: "Urdu (اردو)",
}

# Unicode Script ranges for Indian languages
UNICODE_RANGES = {
    SupportedLanguage.HINDI: re.compile(r"[\u0900-\u097F]"),      # Devanagari
    SupportedLanguage.BENGALI: re.compile(r"[\u0980-\u09FF]"),    # Bengali
    SupportedLanguage.PUNJABI: re.compile(r"[\u0A00-\u0A7F]"),    # Gurmukhi
    SupportedLanguage.GUJARATI: re.compile(r"[\u0A80-\u0AFF]"),   # Gujarati
    SupportedLanguage.TAMIL: re.compile(r"[\u0B80-\u0BFF]"),      # Tamil
    SupportedLanguage.TELUGU: re.compile(r"[\u0C00-\u0C7F]"),     # Telugu
    SupportedLanguage.KANNADA: re.compile(r"[\u0C80-\u0CFF]"),    # Kannada
    SupportedLanguage.MALAYALAM: re.compile(r"[\u0D00-\u0D7F]"),  # Malayalam
    SupportedLanguage.URDU: re.compile(r"[\u0600-\u06FF]"),       # Arabic / Urdu
}


def detect_language(text: str) -> SupportedLanguage:
    """Detect language from text Unicode script patterns; defaults to English."""
    for lang, pattern in UNICODE_RANGES.items():
        if pattern.search(text):
            return lang
    return SupportedLanguage.ENGLISH


LOCALIZED_TEMPLATES: Dict[SupportedLanguage, Dict[str, str]] = {
    SupportedLanguage.ENGLISH: {
        "greeting": "Hello {name}! You are logged in as {role}. How can I assist you today?",
        "attendance_student": "Your current attendance is {percentage:.1f}%.",
        "attendance_child": "{name}'s current attendance is {percentage:.1f}%.",
        "attendance_marked": "Attendance recorded: {name} marked as {status} for {date}.",
        "permission_denied": "I’m sorry, but you do not have permission to perform this action.",
        "clarification_child": "Sure. Which child would you like me to check — {names}?",
        "escalation_submitted": "Your support request has been submitted with Ticket #{ticket_id}. Our staff will contact you shortly."
    },
    SupportedLanguage.HINDI: {
        "greeting": "नमस्ते {name}! आप {role} के रूप में लॉग इन हैं। आज मैं आपकी क्या सहायता कर सकता हूँ?",
        "attendance_student": "आपकी वर्तमान उपस्थिति {percentage:.1f}% है।",
        "attendance_child": "{name} की वर्तमान उपस्थिति {percentage:.1f}% है।",
        "attendance_marked": "उपस्थिति दर्ज: {name} को {date} के लिए {status} चिह्नित किया गया।",
        "permission_denied": "क्षमा करें, आपके पास यह कार्रवाई करने की अनुमति नहीं है।",
        "clarification_child": "ज़रूर। आप किस बच्चे की उपस्थिति देखना चाहते हैं — {names}?",
        "escalation_submitted": "आपका अनुरोध टिकट #{ticket_id} के साथ दर्ज कर लिया गया है। विद्यालय कर्मचारी शीघ्र संपर्क करेंगे।"
    },
    SupportedLanguage.TAMIL: {
        "greeting": "வணக்கம் {name}! நீங்கள் {role} ஆக உள்நுழைந்துள்ளீர்கள். இன்று நான் உங்களுக்கு எவ்வாறு உதவ முடியும்?",
        "attendance_student": "உங்கள் தற்போதைய வருகை {percentage:.1f}%.",
        "attendance_child": "{name}-ன் தற்போதைய வருகை {percentage:.1f}%.",
        "attendance_marked": "வருகை பதிவு செய்யப்பட்டது: {name} {date}-ல் {status} என குறிக்கப்பட்டது.",
        "permission_denied": "மன்னிக்கவும், இந்த செயலைச் செய்ய உங்களுக்கு அனுமதி இல்லை.",
        "clarification_child": "நிச்சயமாக. நீங்கள் எந்த குழந்தையின் வருகையை பார்க்க விரும்புகிறீர்கள் — {names}?",
        "escalation_submitted": "உங்கள் கோரிக்கை டிக்கெட் #{ticket_id} உடன் பதிவு செய்யப்பட்டுள்ளது. பள்ளி ஊழியர்கள் விரைவில் உங்களை தொடர்புகொள்வார்கள்."
    },
    SupportedLanguage.TELUGU: {
        "greeting": "నమస్కారం {name}! మీరు {role} గా లాగిన్ అయ్యారు. ఈరోజు నేను మీకు ఎలా సహాయపడగలను?",
        "attendance_student": "మీ ప్రస్తుత హాజరు శాతం {percentage:.1f}%.",
        "attendance_child": "{name} ప్రస్తుత హాజరు శాతం {percentage:.1f}%.",
        "attendance_marked": "హాజరు నమోదైంది: {name} {date} తేదీన {status} గా గుర్తించబడింది.",
        "permission_denied": "క్షమించండి, ఈ చర్యను చేయడానికి మీకు అనుమతి లేదు.",
        "clarification_child": "తప్పకుండా. మీరు ఏ విద్యార్థి హాజరు చూడాలనుకుంటున్నారు — {names}?",
        "escalation_submitted": "మీ అభ్యర్థన టికెట్ #{ticket_id} తో నమోదు చేయబడింది. సిబ్బంది త్వరలో మిమ్మల్ని సంప్రదిస్తారు."
    },
    SupportedLanguage.MARATHI: {
        "greeting": "नमस्कार {name}! आपण {role} म्हणून लॉग इन आहात. मी आज आपली काय मदत करू शकतो?",
        "attendance_student": "आपली सद्य उपस्थिती {percentage:.1f}% आहे.",
        "attendance_child": "{name} ची सद्य उपस्थिती {percentage:.1f}% आहे.",
        "attendance_marked": "उपस्थिती नोंदवली गेली: {name} यांना {date} साठी {status} नोंदवले आहे.",
        "permission_denied": "क्षमस्व, आपणास ही कृती करण्याची परवानगी नाही.",
        "clarification_child": "नक्कीच. आपण कोणत्या विद्यार्थ्याची माहिती पाहू इच्छिता — {names}?",
        "escalation_submitted": "आपली विनंती तिकीट #{ticket_id} सह नोंदवली गेली आहे. शाळा कर्मचारी लवकरच संपर्क करतील."
    },
    SupportedLanguage.BENGALI: {
        "greeting": "নমস্কার {name}! আপনি {role} হিসেবে লগইন করেছেন। আমি আপনাকে কীভাবে সাহায্য করতে পারি?",
        "attendance_student": "আপনার বর্তমান উপস্থিতি {percentage:.1f}%।",
        "attendance_child": "{name}-এর বর্তমান উপস্থিতি {percentage:.1f}%।",
        "attendance_marked": "উপস্থিতি নথিভুক্ত: {name}-কে {date}-এর জন্য {status} চিহ্নিত করা হয়েছে।",
        "permission_denied": "দুঃখিত, এই কাজটি করার অনুমতি আপনার নেই।",
        "clarification_child": "অবশ্যই। আপনি কোন সন্তানের উপস্থিতি দেখতে চান — {names}?",
        "escalation_submitted": "আপনার অনুরোধটি টিকিট #{ticket_id}-এ নথিভুক্ত হয়েছে। বিদ্যালয় কর্তৃপক্ষ শীঘ্রই যোগাযোগ করবে।"
    },
    SupportedLanguage.GUJARATI: {
        "greeting": "નમસ્તે {name}! તમે {role} તરીકે લૉગ ઇન છો. હું તમારી કેવી રીતે મદદ કરી શકું?",
        "attendance_student": "તમારી વર્તમાન હાજરી {percentage:.1f}% છે.",
        "attendance_child": "{name}ની વર્તમાન હાજરી {percentage:.1f}% છે.",
        "attendance_marked": "હાજરી નોંધાઈ: {name} માટે {date} તારીખે {status} ચિહ્નિત કરવામાં આવ્યું.",
        "permission_denied": "માફ કરશો, તમને આ કાર્ય કરવાની પરવાનગી નથી.",
        "clarification_child": "ચોક્કસ. તમે કયા બાળકની હાજરી તપાસવા માંગો છો — {names}?",
        "escalation_submitted": "તમારી વિનંતી ટિકિટ #{ticket_id} સાથે નોંધાઈ ગઈ છે. શાળા સ્ટાફ ટૂંક સમયમાં સંપર્ક કરશે."
    },
    SupportedLanguage.PUNJABI: {
        "greeting": "ਸਤਿ ਸ੍ਰੀ ਅਕਾਲ {name}! ਤੁਸੀਂ {role} ਵਜੋਂ ਲੌਗਇਨ ਹੋ। ਮੈਂ ਤੁਹਾਡੀ ਕੀ ਮਦਦ ਕਰ ਸਕਦਾ ਹਾਂ?",
        "attendance_student": "ਤੁਹਾਡੀ ਮੌਜੂਦਾ ਹਾਜ਼ਰੀ {percentage:.1f}% ਹੈ।",
        "attendance_child": "{name} ਦੀ ਮੌਜੂਦਾ ਹਾਜ਼ਰੀ {percentage:.1f}% ਹੈ।",
        "attendance_marked": "ਹਾਜ਼ਰੀ ਦਰਜ: {name} ਨੂੰ {date} ਲਈ {status} ਮਾਰਕ ਕੀਤਾ ਗਿਆ।",
        "permission_denied": "ਮਾਫ਼ ਕਰਨਾ, ਤੁਹਾਨੂੰ ਇਹ ਕਾਰਵਾਈ ਕਰਨ ਦੀ ਇਜਾਜ਼ਤ ਨਹੀਂ ਹੈ।",
        "clarification_child": "ਜ਼ਰੂਰ। ਤੁਸੀਂ ਕਿਸ ਬੱਚੇ ਦੀ ਹਾਜ਼ਰੀ ਦੇਖਣਾ ਚਾਹੁੰਦੇ ਹੋ — {names}?",
        "escalation_submitted": "ਤੁਹਾਡੀ ਬੇਨਤੀ ਟਿਕਟ #{ticket_id} ਨਾਲ ਦਰਜ ਕਰ ਲਈ ਗਈ ਹੈ।"
    },
    SupportedLanguage.KANNADA: {
        "greeting": "ನಮಸ್ಕಾರ {name}! ನೀವು {role} ಆಗಿ ಲಾಗ್ ಇನ್ ಆಗಿದ್ದೀರಿ. ನಾನು ನಿಮಗೆ ಹೇಗೆ ಸಹಾಯ ಮಾಡಬಹುದು?",
        "attendance_student": "ನಿಮ್ಮ ಪ್ರಸ್ತುತ ಹಾಜರಾತಿ {percentage:.1f}%.",
        "attendance_child": "{name} ರವರ ಪ್ರಸ್ತುತ ಹಾಜರಾತಿ {percentage:.1f}%.",
        "attendance_marked": "ಹಾಜರಾತಿ ದಾಖಲಾಗಿದೆ: {name} ರವರಿಗೆ {date} ರಂದು {status} ಎಂದು ನಮೂದಿಸಲಾಗಿದೆ.",
        "permission_denied": "ಕ್ಷಮಿಸಿ, ಈ ಕ್ರಿಯೆಯನ್ನು ನಿರ್ವಹಿಸಲು ನಿಮಗೆ ಅನುಮತಿಯಿಲ್ಲ.",
        "clarification_child": "ಖಂಡಿತ. ನೀವು ಯಾವ ಮಗುವಿನ ಹಾಜರಾತಿಯನ್ನು ಪರಿಶೀಲಿಸಲು ಬಯಸುತ್ತೀರಿ — {names}?",
        "escalation_submitted": "ನಿಮ್ಮ ವಿನಂತಿಯನ್ನು ಟಿಕೆಟ್ #{ticket_id} ನೊಂದಿಗೆ ಸಲ್ಲಿಸಲಾಗಿದೆ."
    },
    SupportedLanguage.MALAYALAM: {
        "greeting": "നമസ്കാരം {name}! നിങ്ങൾ {role} ആയി ലോഗിൻ ചെയ്തിരിക്കുന്നു. ഞാൻ എങ്ങനെ സഹായിക്കണം?",
        "attendance_student": "നിങ്ങളുടെ നിലവിലെ ഹാജർ {percentage:.1f}% ആണ്.",
        "attendance_child": "{name}-ന്റെ നിലവിലെ ഹാജർ {percentage:.1f}% ആണ്.",
        "attendance_marked": "ഹാജർ രേഖപ്പെടുത്തി: {name}-ന് {date}-ൽ {status} എന്ന് രേഖപ്പെടുത്തി.",
        "permission_denied": "ക്ഷമിക്കണം, ഈ പ്രവർത്തനം നടത്താൻ നിങ്ങൾക്ക് അനുമതിയില്ല.",
        "clarification_child": "തീർച്ചയായും. ഏത് കുട്ടിയുടെ ഹാജർ ആണ് പരിശോധിക്കേണ്ടത് — {names}?",
        "escalation_submitted": "നിങ്ങളുടെ അഭ്യർത്ഥന ടിക്കറ്റ് #{ticket_id} ആയി സമർപ്പിച്ചിരിക്കുന്നു."
    },
    SupportedLanguage.URDU: {
        "greeting": "آداب {name}! آپ بطور {role} لاگ ان ہیں۔ میں آپ کی کیا مدد کر سکتا ہوں؟",
        "attendance_student": "آپ کی موجودہ حاضری {percentage:.1f} فیصد ہے۔",
        "attendance_child": "{name} کی موجودہ حاضری {percentage:.1f} فیصد ہے۔",
        "attendance_marked": "حاضری درج کی گئی: {name} کو {date} کے لیے {status} نشان زد کیا گیا۔",
        "permission_denied": "معذرت، آپ کو اس کارروائی کی اجازت نہیں ہے۔",
        "clarification_child": "یقیناً۔ آپ کس بچے کی حاضری معلوم کرنا چاہتے ہیں — {names}؟",
        "escalation_submitted": "آپ کی درخواست ٹکٹ #{ticket_id} کے ساتھ جمع کر دی گئی ہے۔"
    }
}


def format_localized_message(
    template_key: str,
    language: SupportedLanguage = SupportedLanguage.ENGLISH,
    **kwargs
) -> str:
    """Format template message into requested language with English fallback."""
    lang_templates = LOCALIZED_TEMPLATES.get(language, LOCALIZED_TEMPLATES[SupportedLanguage.ENGLISH])
    template = lang_templates.get(template_key) or LOCALIZED_TEMPLATES[SupportedLanguage.ENGLISH].get(template_key, "")
    try:
        return template.format(**kwargs)
    except Exception:
        return template
