"""Tests for the language detection service.

Covers:
- French detection
- Arabic standard detection
- Darija (Arabic-script) detection
- Darija (Latin-script / Arabizi) detection
- Edge cases (empty, mixed, short messages)
"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from services.language_service import detect_language, _check_darija_markers


# ============================================================
# French detection
# ============================================================

class TestFrenchDetection:
    """Test French language detection."""

    def test_simple_french(self):
        result = detect_language("Bonjour, comment ça va ?")
        assert result.detected_lang == "fr"
        assert result.is_darija is False

    def test_french_cyberviolence(self):
        result = detect_language("Je suis victime de cyberharcèlement, que dois-je faire ?")
        assert result.detected_lang == "fr"

    def test_french_legal(self):
        result = detect_language("Quels sont mes droits selon la loi 103-13 ?")
        assert result.detected_lang == "fr"

    def test_french_help_request(self):
        result = detect_language("J'ai besoin d'aide, quelqu'un me menace en ligne")
        assert result.detected_lang == "fr"

    @pytest.mark.parametrize(
        "message",
        [
            "Je suis victime d'intimidation en ligne",
            "Que faire afin de me protéger ?",
            "La fin du harcèlement est mon objectif",
        ],
    )
    def test_french_words_do_not_match_darija_substrings(self, message):
        result = detect_language(message)
        assert result.detected_lang == "fr"
        assert result.is_darija is False


# ============================================================
# Arabic standard detection
# ============================================================

class TestArabicDetection:
    """Test Arabic standard language detection."""

    def test_arabic_standard(self):
        result = detect_language("أنا ضحية ابتزاز جنسي، ماذا أفعل؟")
        assert result.detected_lang == "ar"

    def test_arabic_help_request(self):
        result = detect_language("أريد رقم الشرطة للإبلاغ عن تحرش إلكتروني")
        assert result.detected_lang == "ar"

    def test_arabic_legal(self):
        result = detect_language("ما هي العقوبات المنصوص عليها في القانون المغربي؟")
        assert result.detected_lang == "ar"


# ============================================================
# Darija detection (Arabic script)
# ============================================================

class TestDarijaDetection:
    """Test Moroccan Darija detection."""

    def test_darija_basic(self):
        result = detect_language("واش نقدر نقدم شكاية؟")
        assert result.detected_lang == "ar"
        assert result.is_darija is True

    def test_darija_threat(self):
        result = detect_language("كيفاش نبلغ على واحد كيهددني؟")
        assert result.detected_lang == "ar"
        assert result.is_darija is True

    def test_darija_help(self):
        result = detect_language("أش ندير باش نحمي راسي من التحرش؟")
        assert result.detected_lang == "ar"
        assert result.is_darija is True

    def test_darija_with_hchouma(self):
        result = detect_language("حشومة نگول لشي واحد، ماشي ساهل")
        assert result.detected_lang == "ar"
        assert result.is_darija is True


# ============================================================
# Darija Latin-script (Arabizi) detection
# ============================================================

class TestDarijaLatinDetection:
    """Test Darija in Latin script (Arabizi)."""

    def test_arabizi_basic(self):
        result = detect_language("wach n9der n9dem chkaya?")
        assert result.detected_lang == "ar"
        assert result.is_darija is True

    def test_arabizi_help(self):
        result = detect_language("kifach ndir bach nblagh?")
        assert result.detected_lang == "ar"
        assert result.is_darija is True

    def test_arabizi_requires_complete_marker_word(self):
        result = detect_language("intimidation")
        assert result.detected_lang == "fr"
        assert result.is_darija is False

    def test_common_arabizi_words(self):
        result = detect_language("salam, chno ndir daba?")
        assert result.detected_lang == "ar"
        assert result.is_darija is True

    def test_emotional_arabizi_words(self):
        result = detect_language("ana m9hora o kanbki bzaf")
        assert result.detected_lang == "ar"
        assert result.is_darija is True


# ============================================================
# Edge cases
# ============================================================

class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_string(self):
        result = detect_language("")
        assert result.detected_lang == "fr"
        assert result.confidence == 0.0

    def test_whitespace_only(self):
        result = detect_language("   ")
        assert result.detected_lang == "fr"
        assert result.confidence == 0.0

    def test_short_french(self):
        result = detect_language("Aide")
        assert result.detected_lang == "fr"

    def test_numbers_only(self):
        result = detect_language("19 177 2511")
        assert result.detected_lang == "fr"

    def test_confidence_present(self):
        result = detect_language("Je suis en danger")
        assert 0.0 <= result.confidence <= 1.0


# ============================================================
# Darija marker scoring
# ============================================================

class TestDarijaMarkerScoring:
    """Test the Darija marker scoring function."""

    def test_no_markers(self):
        score = _check_darija_markers("هذا نص عربي فصيح")
        # May or may not have markers; just verify it doesn't crash
        assert 0.0 <= score <= 1.0

    def test_single_marker_short(self):
        score = _check_darija_markers("واش هذا صحيح؟")
        assert score >= 0.3  # Single marker in short text should be enough

    def test_multiple_markers(self):
        score = _check_darija_markers("واش كيفاش ندير باش نبلغ على هاد الشخص")
        assert score >= 0.5  # Multiple markers = high confidence
