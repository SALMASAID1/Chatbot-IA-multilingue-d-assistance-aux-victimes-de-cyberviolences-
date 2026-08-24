"""Language detection service for FR / Arabic Standard / Darija.

Uses the input script as the primary FR/AR signal, then applies a
Darija-specific heuristic layer. Latin text defaults to French unless
complete Arabizi/Darija words are present; Arabic-script text routes to
Arabic.

Darija routes through "ar" in the RAG pipeline since the AR knowledge
base already mixes standard Arabic and Darija content.
"""
import re
from dataclasses import dataclass


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
    "chno", "chnou", "kayn", "kayna", "3afak", "7it", "m3a",
    "chokran", "salam",
    # Emotional Darija / Arabizi
    "khayf", "khayfa", "mkhlo3", "mkhlo3a", "m9lo9", "m9l9",
    "mkhno9", "mkhno9a", "m9hor", "m9hora", "ta3bt", "kanbki",
    "bo7di", "day3", "day3a", "ma9dertch",
]

# These spellings are also valid/common French words. They must never be
# enough on their own to classify a Latin-script message as Darija.
DARIJA_AMBIGUOUS_LATIN = {"fin"}


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


def _arabic_tokens(text: str) -> list[str]:
    """Return Arabic-script words without punctuation."""
    return re.findall(r"[\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF]+", text)


def _latin_tokens(text: str) -> list[str]:
    """Return lowercase Latin/Arabizi words without punctuation."""
    return re.findall(r"[a-zà-öø-ÿ0-9]+", text.lower())


def _latin_darija_markers(text: str) -> set[str]:
    """Find complete Arabizi words, never substrings inside French words."""
    tokens = set(_latin_tokens(text))
    return tokens.intersection(DARIJA_MARKERS_LATIN)


def _check_darija_markers(text: str) -> float:
    """
    Check for Darija markers in the text.

    Returns a score (0.0-1.0) indicating how likely the text is Darija.
    Score > 0.3 is considered Darija.
    """
    arabic_matches = set(_arabic_tokens(text)).intersection(DARIJA_MARKERS_AR)
    latin_matches = _latin_darija_markers(text)
    total_markers_found = len(arabic_matches) + len(latin_matches)

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

    Deterministic process:
    1. Any Arabic-script text routes to Arabic.
    2. Latin-script text routes to Darija only when a complete, unambiguous
       Arabizi marker is present.
    3. All other Latin-script text defaults to French.

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

    # Arabic script always selects the Arabic response pipeline. Darija in
    # Arabic script remains distinguishable through the marker score.
    if _has_arabic_chars(text):
        darija_score = _check_darija_markers(text)
        return LanguageResult(
            detected_lang="ar",
            is_darija=darija_score >= 0.3,
            confidence=1.0,
            raw_detection="arabic_script",
        )

    # Latin script defaults to French. Only complete, unambiguous Darija
    # words can switch it to the Arabic/Darija response pipeline.
    latin_matches = _latin_darija_markers(text)
    strong_matches = latin_matches - DARIJA_AMBIGUOUS_LATIN
    if strong_matches:
        return LanguageResult(
            detected_lang="ar",
            is_darija=True,
            confidence=min(0.7 + (0.1 * len(strong_matches)), 1.0),
            raw_detection="darija_latin",
        )

    return LanguageResult(
        detected_lang="fr",
        is_darija=False,
        confidence=0.9,
        raw_detection="latin_default_fr",
    )
