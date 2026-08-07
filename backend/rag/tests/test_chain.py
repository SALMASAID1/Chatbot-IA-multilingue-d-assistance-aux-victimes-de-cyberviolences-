"""Unit tests for the RAG chain, urgency detection, and profile detection."""
import pytest
from pathlib import Path

import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from config import GOOGLE_API_KEY


class TestUrgencyDetection:
    """Tests for urgency keyword detection -- no API key required."""

    def test_detect_urgency_fr_danger(self):
        from rag.chain import detect_urgency
        assert detect_urgency("Je suis en danger", "fr") is True

    def test_detect_urgency_fr_suicide(self):
        from rag.chain import detect_urgency
        assert detect_urgency("J'ai envie de mourir", "fr") is True

    def test_detect_urgency_fr_normal(self):
        from rag.chain import detect_urgency
        assert detect_urgency("Qu'est-ce que la cyberviolence ?", "fr") is False

    def test_detect_urgency_ar_danger(self):
        from rag.chain import detect_urgency
        assert detect_urgency("\u0623\u0646\u0627 \u0641 \u062e\u0637\u0631", "ar") is True

    def test_detect_urgency_ar_normal(self):
        from rag.chain import detect_urgency
        assert detect_urgency("\u0645\u0627 \u0647\u0648 \u0627\u0644\u0639\u0646\u0641 \u0627\u0644\u0631\u0642\u0645\u064a", "ar") is False

    def test_detect_urgency_case_insensitive(self):
        from rag.chain import detect_urgency
        assert detect_urgency("JE SUIS EN DANGER", "fr") is True
        assert detect_urgency("URGENCE", "fr") is True


class TestProfileDetection:
    """Tests for user profile detection -- no API key required."""

    def test_detect_victim_default(self):
        from rag.chain import detect_profile
        assert detect_profile("Je suis victime de cyberharcelement", "fr") == "victim"

    def test_detect_parent_profile(self):
        from rag.chain import detect_profile
        assert detect_profile("Mon enfant est harcele en ligne", "fr") == "parent"

    def test_detect_parent_profile_fille(self):
        from rag.chain import detect_profile
        assert detect_profile("Ma fille recoit des messages menacants", "fr") == "parent"

    def test_detect_enseignant_profile(self):
        from rag.chain import detect_profile
        assert detect_profile("Je suis enseignant, un eleve est harcele", "fr") == "enseignant"

    def test_detect_enseignant_prof(self):
        from rag.chain import detect_profile
        assert detect_profile("En tant que prof, que faire ?", "fr") == "enseignant"

    def test_detect_temoin_profile(self):
        from rag.chain import detect_profile
        assert detect_profile("Je suis temoin de harcelement", "fr") == "temoin"

    def test_detect_jeune_profile(self):
        from rag.chain import detect_profile
        assert detect_profile("Je suis mineur, que faire ?", "fr") == "jeune"

    def test_detect_detresse_emotionnelle(self):
        from rag.chain import detect_profile
        assert detect_profile("Je suis en panique, je tremble", "fr") == "detresse_emotionnelle"

    def test_detect_detresse_honte(self):
        from rag.chain import detect_profile
        assert detect_profile("J'ai tellement honte, hchouma", "fr") == "detresse_emotionnelle"

    def test_detresse_prioritized_over_victim(self):
        """Emotional distress should be detected even when victim keywords present."""
        from rag.chain import detect_profile
        result = detect_profile("Je suis victime et je suis en panique", "fr")
        assert result == "detresse_emotionnelle"

    def test_detect_parent_ar(self):
        from rag.chain import detect_profile
        assert detect_profile("\u0648\u0644\u062f\u064a \u0643\u064a\u062a\u0639\u0631\u0636 \u0644\u0644\u062a\u0646\u0645\u0631", "ar") == "parent"

    def test_detect_detresse_ar(self):
        from rag.chain import detect_profile
        assert detect_profile("\u062e\u0627\u064a\u0641 \u0628\u0632\u0627\u0641", "ar") == "detresse_emotionnelle"


# Skip API-dependent tests if no key configured
pytestmark_api = pytest.mark.skipif(
    not GOOGLE_API_KEY or GOOGLE_API_KEY == "your-gemini-api-key-here",
    reason="GOOGLE_API_KEY not configured in .env"
)


@pytest.fixture(scope="module")
def chain():
    """Fixture: initialize the RAG chain once for all tests."""
    from rag.chain import RAGChain
    return RAGChain()


@pytestmark_api
class TestRAGChain:
    def test_ask_fr_returns_answer(self, chain):
        result = chain.ask("Qu'est-ce que la sextorsion ?", langue="fr")
        assert "answer" in result
        assert len(result["answer"]) > 0
        assert result["langue"] == "fr"

    def test_ask_ar_returns_answer(self, chain):
        result = chain.ask(
            "\u0645\u0627 \u0647\u0648 \u0627\u0644\u0627\u0628\u062a\u0632\u0627\u0632 \u0627\u0644\u062c\u0646\u0633\u064a\u061f",
            langue="ar"
        )
        assert "answer" in result
        assert len(result["answer"]) > 0

    def test_response_includes_sources(self, chain):
        result = chain.ask("Je suis victime de cyberharcelement", langue="fr")
        assert "sources" in result
        assert isinstance(result["sources"], list)

    def test_response_includes_profile(self, chain):
        result = chain.ask("Mon enfant est harcele", langue="fr")
        assert "user_profile" in result
        assert result["user_profile"] == "parent"

    def test_urgent_message_flagged(self, chain):
        result = chain.ask("Je suis en danger", langue="fr")
        assert result["is_urgent"] is True

    def test_normal_message_not_flagged(self, chain):
        result = chain.ask("Comment securiser mon compte ?", langue="fr")
        assert result["is_urgent"] is False

    def test_reset_history(self, chain):
        chain.ask("Bonjour", langue="fr")
        assert len(chain.conversation_history) > 0
        chain.reset_history()
        assert len(chain.conversation_history) == 0
