"""Language detection service for FR / Arabic Standard / Darija.

Uses `langdetect` as the primary detector for FR vs AR, then applies
a Darija-specific heuristic layer when Arabic is detected.

Darija routes through "ar" in the RAG pipeline since the AR knowledge
base already mixes standard Arabic and Darija content.
"""
import re
from dataclasses import dataclass
from typing import Optional

from langdetect import detect, detect_langs, LangDetectException


# ============================================================
# Darija markers — common words/patterns that distinguish
# Moroccan Darija from Modern Standard Arabic (MSA)
# ============================================================

# Arabic-script Darija markers
DARIJA_MARKERS_AR = [
    # Interrogatives
    "واش", "كيفاش", "علاش", "فين", "شحال", "أشنو", "أش",
    "فوقاش", "شكون", "منين",
    # Common verbs/expressions
    "كنبغي", "كنقدر", "كندير", "كنعرف", "كنحس", "كنخاف",
    "بغيت", "نقدر", "ندير", "نعرف",
    "ديال", "ديالي", "ديالك",
    "غادي", "غادا",
    "ماشي", "والو", "بزاف", "شوية",
    "كيدير", "كتدير", "كيقول", "كتقول",
    # Pronouns/particles unique to Darija
    "نتا", "نتي", "حنا", "نتوما", "هوما",
    "فحال", "بحال", "هاد", "هادي", "هادو",
    "راه", "راها", "راهم",
    "عندي", "عندك", "عندو", "عندها",
    "ولا", "يالاه", "دابا",
]

# Latin-script Darija (Arabizi) markers
DARIJA_MARKERS_LATIN = [
    "wach", "kifach", "3lach", "fin", "chhal", "achno",
    "bghit", "n9der", "ndir", "dyal", "dyali",
    "ghadi", "machi", "walou", "bzaf", "chwia",
    "hada", "hadi", "rah", "raha",
    "labas", "hamdoulah", "inchallah", "nta", "nti",
]


@dataclass
class LanguageResult:
    """Result of language detection."""
    detected_lang: str          # "fr" or "ar" (maps to RAG pipeline)
    is_darija: bool             # True if Darija was detected
    confidence: float           # Detection confidence (0.0-1.0)
    raw_detection: str          # Raw langdetect output before mapping


def _has_arabic_chars(text: str) -> bool:
    """Check if text contains Arabic script characters."""
    return bool(re.search(r'[\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF]', text))


def _check_darija_markers(text: str) -> float:
    """
    Check for Darija markers in the text.

    Returns a score (0.0-1.0) indicating how likely the text is Darija.
    Score > 0.3 is considered Darija.
    """
    text_lower = text.lower()
    total_markers_found = 0
    total_markers = len(DARIJA_MARKERS_AR) + len(DARIJA_MARKERS_LATIN)

    # Check Arabic-script markers
    for marker in DARIJA_MARKERS_AR:
        if marker in text:
            total_markers_found += 1

    # Check Latin-script markers
    for marker in DARIJA_MARKERS_LATIN:
        if marker in text_lower:
            total_markers_found += 1

    if total_markers == 0:
        return 0.0

    # Normalize: even 1-2 markers in a short message is a strong signal
    # Weight by message length (shorter messages need fewer markers)
    words_count = max(len(text.split()), 1)
    if words_count <= 5:
        # Short message: 1 marker is enough
        return min(total_markers_found / 1.0, 1.0)
    elif words_count <= 15:
        # Medium message: 2 markers is strong
        return min(total_markers_found / 2.0, 1.0)
    else:
        # Long message: need 3+ markers
        return min(total_markers_found / 3.0, 1.0)


def detect_language(text: str) -> LanguageResult:
    """
    Detect the language of the input text.

    Two-step process:
    1. Use langdetect for primary FR/AR classification
    2. If AR detected, apply Darija heuristics

    Args:
        text: User input message

    Returns:
        LanguageResult with detected language, Darija flag, and confidence
    """
    if not text or not text.strip():
        return LanguageResult(
            detected_lang="fr",
            is_darija=False,
            confidence=0.0,
            raw_detection="empty",
        )

    text = text.strip()

    # Step 1: Check for Latin-script Darija (Arabizi) first
    darija_latin_score = 0
    text_lower = text.lower()
    for marker in DARIJA_MARKERS_LATIN:
        if marker in text_lower:
            darija_latin_score += 1

    if darija_latin_score >= 1 and not _has_arabic_chars(text):
        # Latin-script Darija detected
        return LanguageResult(
            detected_lang="ar",
            is_darija=True,
            confidence=min(darija_latin_score / 2.0, 1.0),
            raw_detection="darija_latin",
        )

    # Step 2: Use langdetect for primary classification
    try:
        lang_results = detect_langs(text)
        primary = lang_results[0]
        raw_lang = primary.lang
        confidence = primary.prob
    except LangDetectException:
        # If detection fails, check for Arabic chars as fallback
        if _has_arabic_chars(text):
            raw_lang = "ar"
            confidence = 0.5
        else:
            raw_lang = "fr"
            confidence = 0.5

    # Step 3: Map to supported languages
    if raw_lang == "ar":
        detected_lang = "ar"
    elif raw_lang == "fr":
        detected_lang = "fr"
    else:
        # Unsupported language — default based on script
        if _has_arabic_chars(text):
            detected_lang = "ar"
        else:
            detected_lang = "fr"
        confidence = max(confidence * 0.5, 0.3)

    # Step 4: If Arabic detected, check for Darija
    is_darija = False
    if detected_lang == "ar":
        darija_score = _check_darija_markers(text)
        if darija_score >= 0.3:
            is_darija = True

    return LanguageResult(
        detected_lang=detected_lang,
        is_darija=is_darija,
        confidence=round(confidence, 3),
        raw_detection=raw_lang,
    )
