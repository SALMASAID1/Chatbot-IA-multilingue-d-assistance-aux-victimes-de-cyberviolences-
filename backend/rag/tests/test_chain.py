"""Unit tests for the RAG chain, urgency detection, and profile detection."""
import os
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


# Latin-script Darija. language_service routes these to "ar" whenever it finds
# a Darija marker, and to "fr" otherwise, so both routings are exercised.
ARABIZI_URGENT = [
    "bghit nmot",
    "bghit nmout",
    "ma bghitch n3ich walakin nmut",
    "n9tel rasi",
    "nqtel rassi",
    "nktel rasi",
    "ma bqach 3andi la9wa",
    "mab9ach 3andi la9wa",
    "3yit mn 7yati",
    "3ayit men 7yati",
    "bghit nsali 7yati",
    "ana f khatar",
    "rah f lkhatar",
    "ghadi ydrebni daba",
    "ghadi y9telni",
    "rah 3end bab dar",
]

# Ordinary questions that must never trigger the emergency protocol: it
# bypasses retrieval and the LLM and answers with phone numbers only.
ARABIZI_NOT_URGENT = [
    "wach ndir plainte f police ?",
    "kifach n9der nsali had lmochkil ?",
    "bghit n3raf chnou hiya lqanoun 103-13",
    "3afak 3awnini bach nbdel password dyali",
    "chhal khass bach ndir signalement",
    "nta 3andek chi ma3loumat 3la E-Blagh ?",
    "hadi bnt khti kayn chi wa7ed kaydir liha des menaces",
    "Comment signaler un compte Instagram ?",
    "Je ne sais pas quoi faire, un mot de passe a ete vole",
    "Bien motive, je veux porter plainte",
]


class TestArabiziUrgencyDetection:
    """Latin-script Darija urgency -- no API key required.

    Regression guard: `detect_urgency("bghit nmot", "ar")` returned False
    while the Arabic-script spelling returned True, so a victim typing
    suicidal ideation in Arabizi never reached the emergency protocol.
    """

    @pytest.mark.parametrize("message", ARABIZI_URGENT)
    def test_arabizi_urgency_detected_in_both_pipelines(self, message):
        from rag.chain import detect_urgency
        assert detect_urgency(message, "ar") is True
        assert detect_urgency(message, "fr") is True

    @pytest.mark.parametrize("message", ARABIZI_NOT_URGENT)
    def test_ordinary_messages_stay_non_urgent(self, message):
        from rag.chain import detect_urgency
        assert detect_urgency(message, "ar") is False
        assert detect_urgency(message, "fr") is False

    def test_matches_the_arabic_script_spelling(self):
        """Arabizi and Arabic script must agree on the same sentence."""
        from rag.chain import detect_urgency
        assert detect_urgency("bghit nmot", "ar") is True
        assert detect_urgency("\u0628\u063a\u064a\u062a \u0646\u0645\u0648\u062a", "ar") is True

    def test_word_boundaries_are_enforced(self):
        """Short Arabizi tokens must not fire inside a longer word."""
        from rag.chain import detect_urgency
        assert detect_urgency("nmotive", "ar") is False
        assert detect_urgency("anmot", "ar") is False
        assert detect_urgency("nmot123", "ar") is False

    def test_french_keywords_reach_the_arabic_pipeline(self):
        """Darija speakers code-switch: Latin-script French must still count."""
        from rag.chain import detect_urgency
        assert detect_urgency("wach kayn chi urgence", "ar") is True
        assert detect_urgency("rah f danger", "ar") is True

    def test_arabic_script_is_unaffected_by_the_french_pass(self):
        """A pure Arabic-script message keeps its previous behaviour."""
        from rag.chain import detect_urgency
        assert detect_urgency("\u0645\u0627 \u0647\u0648 \u0627\u0644\u0639\u0646\u0641 \u0627\u0644\u0631\u0642\u0645\u064a", "ar") is False

    def test_language_service_routing_still_reaches_urgency(self):
        """End-to-end: whatever language_service decides, urgency is caught."""
        from rag.chain import detect_urgency
        from services.language_service import detect_language
        for message in ARABIZI_URGENT:
            langue = detect_language(message).detected_lang
            assert detect_urgency(message, langue) is True, message


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

    @pytest.mark.parametrize(
        "message",
        [
            "Je suis brisée et je ne sais plus quoi faire",
            "Je me sens détruit depuis cette histoire",
            "Je n'en peux plus, je suis à bout",
            "Je me sens effondré et seul",
        ],
    )
    def test_detects_broken_or_overwhelmed_french_user(self, message):
        from rag.chain import detect_profile

        assert detect_profile(message, "fr") == "detresse_emotionnelle"

    def test_detects_broken_arabic_user(self):
        from rag.chain import detect_profile

        assert detect_profile("أنا منهارة ومخنوقة", "ar") == "detresse_emotionnelle"

    def test_detects_distressed_latin_darija_user(self):
        from rag.chain import detect_profile

        assert detect_profile("ana m9hora o kanbki bzaf", "ar") == "detresse_emotionnelle"


class TestSocialMediaReportingResources:
    """Tests for mandatory reporting when active harm occurs on social media."""

    def test_parent_cyberharassment_requires_priority_reporting(self):
        from rag.chain import needs_social_media_reporting

        assert needs_social_media_reporting(
            "Mon enfant de 13 ans est harcelé sur les réseaux.",
            "fr",
        ) is True

    def test_adult_social_media_harm_requires_priority_reporting(self):
        from rag.chain import needs_social_media_reporting

        assert needs_social_media_reporting(
            "Mes photos ont été publiées sans mon accord sur Telegram.",
            "fr",
        ) is True

    def test_generic_social_media_prevention_does_not_force_reporting(self):
        from rag.chain import needs_social_media_reporting

        assert needs_social_media_reporting(
            "Comment sécuriser mon compte Facebook ?",
            "fr",
        ) is False

    def test_missing_resources_are_appended_with_exact_urls(self):
        from rag.chain import ensure_social_media_reporting

        answer = ensure_social_media_reporting(
            "Je comprends votre inquiétude.",
            "fr",
        )

        assert "Conservez les preuves" in answer
        assert "réseau social" in answer
        assert "https://evigilance.ma/fr/signaler" in answer
        assert "https://www.cyberconfiance.ma" in answer
        assert "2511" not in answer

    def test_onde_is_added_only_for_child_context(self):
        from rag.chain import ensure_social_media_reporting

        answer = ensure_social_media_reporting(
            "Je comprends votre inquiétude.",
            "fr",
            include_onde=True,
        )

        assert "2511" in answer

    def test_existing_resources_are_not_duplicated(self):
        from rag.chain import ensure_social_media_reporting

        answer = (
            "Conservez les preuves et signalez le compte sur le réseau.\n"
            "https://evigilance.ma/fr/signaler\n"
            "https://www.cyberconfiance.ma"
        )

        assert ensure_social_media_reporting(answer, "fr") == answer


class TestEmotionalSupportPriority:
    """Tests that emotional support appears before operational actions."""

    def test_cold_answer_receives_supportive_opening(self):
        from rag.chain import ensure_emotional_support

        answer = ensure_emotional_support(
            "Signalez immédiatement le compte sur la plateforme.",
            "fr",
        )

        assert answer.startswith("Je suis désolé")
        assert answer.index("Je suis désolé") < answer.index("Signalez")

    def test_existing_supportive_opening_is_not_duplicated(self):
        from rag.chain import ensure_emotional_support

        answer = "Je comprends votre douleur. Vous n'êtes pas seul(e)."
        assert ensure_emotional_support(answer, "fr") == answer

    def test_distress_precedes_social_media_reporting_in_final_answer(
        self,
        monkeypatch,
    ):
        from unittest.mock import MagicMock
        from rag import chain as chain_module

        retriever = MagicMock()
        retriever.search_with_fallback.return_value = []
        retriever.format_context.return_value = "Contexte cyberviolence."
        monkeypatch.setattr(chain_module, "BilingualRetriever", lambda: retriever)

        rag_chain = chain_module.RAGChain()
        rag_chain._provider = MagicMock()
        rag_chain._provider.generate.return_value = "Signalez le compte Instagram."

        result = rag_chain.ask(
            "Je suis brisée, mes photos ont été publiées sur Instagram.",
            langue="fr",
        )

        assert result["user_profile"] == "detresse_emotionnelle"
        assert result["answer"].startswith("Je suis désolé")
        assert result["answer"].index("Je suis désolé") < result["answer"].index("Signalez")
        assert "https://evigilance.ma/fr/signaler" in result["answer"]

    def test_parent_cyberharassment_answer_guarantees_resources_and_onde(
        self,
        monkeypatch,
    ):
        from unittest.mock import MagicMock
        from rag import chain as chain_module

        retriever = MagicMock()
        retriever.search_with_fallback.return_value = []
        retriever.format_context.return_value = "Contexte cyberharcelement."
        monkeypatch.setattr(chain_module, "BilingualRetriever", lambda: retriever)

        rag_chain = chain_module.RAGChain()
        rag_chain._provider = MagicMock()
        rag_chain._provider.generate.return_value = (
            "Je comprends votre inquiétude. Conservez les preuves."
        )

        result = rag_chain.ask(
            "Mon enfant de 13 ans est harcelé sur les réseaux. Que faire ?",
            langue="fr",
        )

        assert result["user_profile"] == "parent"
        assert "https://evigilance.ma/fr/signaler" in result["answer"]
        assert "https://www.cyberconfiance.ma" in result["answer"]
        assert "2511" in result["answer"]


# Skip API-dependent tests if no key configured
pytestmark_api = pytest.mark.skipif(
    os.getenv("RUN_LIVE_LLM_TESTS") != "1"
    or not GOOGLE_API_KEY
    or GOOGLE_API_KEY == "your-gemini-api-key-here",
    reason="Set RUN_LIVE_LLM_TESTS=1 to spend quota on live Gemini tests",
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
