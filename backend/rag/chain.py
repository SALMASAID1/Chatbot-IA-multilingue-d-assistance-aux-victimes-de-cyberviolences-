"""Full RAG pipeline: retriever + prompt + Gemini LLM -> contextual response.

Includes (aligned with Mme Belaous feedback):
- Multi-profile detection: victim, parent, teacher, witness, young person
- Emotional weather assessment (meteo des emotions)
- Guided breathing/grounding exercises (interactive, step-by-step)
- Psychoeducation on trauma responses (freeze, hypervigilance, hchouma)
- Urgency detection based on livrable-1 trigger keywords
- Emergency protocol for crisis situations
- Conversation history management
"""
import logging
import re
from typing import Optional, List, Dict

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from config import (
    URGENCY_KEYWORDS_FR, URGENCY_KEYWORDS_AR, URGENCY_KEYWORDS_ARABIZI,
    EMERGENCY_RESPONSE_FR, EMERGENCY_RESPONSE_AR,
)
from llm.gemini_provider import GeminiProvider, get_gemini_provider
from rag.retriever import BilingualRetriever

logger = logging.getLogger(__name__)


# ============================================================
# User profile detection keywords
# Based on livrable-1 mots_cles_declencheurs.md categories Q29-Q32
# ============================================================
PROFILE_KEYWORDS = {
    "parent": {
        "fr": ["parent", "mon enfant", "mon fils", "ma fille", "ado",
               "confisquer ecran", "proteger mon enfant", "inquiet pour"],
        "ar": ["الوالدين", "ولدي", "بنتي", "طفل", "حماية الطفل",
               "حيد التلفون", "قلق على"],
    },
    "enseignant": {
        "fr": ["enseignant", "prof", "professeur", "educateur", "ecole",
               "college", "lycee", "eleve", "etablissement scolaire"],
        "ar": ["أستاذ", "مربي", "مدرسة", "ثانوية", "مؤسسة تعليمية",
               "تلميذ"],
    },
    "temoin": {
        "fr": ["temoin", "j'ai vu", "quelqu'un que je connais", "mon ami",
               "ma copine", "collègue", "que faire si je vois"],
        "ar": ["شاهد", "شفت", "صاحبي", "صاحبتي", "واحد كنعرفو"],
    },
    "jeune": {
        "fr": ["je suis mineur", "j'ai 14 ans", "j'ai 15 ans", "j'ai 16 ans",
               "adolescent", "au college", "au lycee", "sans parents"],
        "ar": ["قاصر", "مراهق", "بلا الوالدين", "عندي 14", "عندي 15"],
    },
    "detresse_emotionnelle": {
        "fr": ["panique", "stress", "anxiete", "peur", "honte", "hchouma",
               "je tremble", "je pleure", "je n'arrive pas", "submerge",
               "bloque", "sideree", "sideration", "choc", "traumatisme",
               "cauchemars", "insomnie", "plus envie"],
        "ar": ["خايف", "خايفة", "حشومة", "قلق", "توتر", "صدمة", "نوبة هلع",
               "كنرتعش", "كنبكي", "ما قدرتش", "نعاس", "مكسور", "مكسورة",
               "محطم", "محطمة", "منهار", "منهارة", "ضايع", "ضايعة",
               "يائس", "يائسة", "تعبت", "بوحدي", "مخنوق", "مخنوقة",
               "mkhlo3", "mkhlo3a", "khayf", "khayfa", "m9lo9", "m9l9",
               "mkhno9", "mkhno9a", "m9hor", "m9hora", "ta3bt", "kanbki",
               "bo7di", "day3", "day3a", "ma9dertch"],
    },
}


EMOTIONAL_DISTRESS_PATTERNS_FR = [
    r"\bpanique",
    r"\bstress(?:e|é|ée)?\b",
    r"\banxi(?:ete|été|eux|euse)\b",
    r"\bpeur\b",
    r"\bhonte\b",
    r"\bhchouma\b",
    r"\bje (?:suis|me sens) (?:bris[ée]e?|d[ée]truit(?:e)?|effondr[ée]e?|perdu(?:e)?|vid[ée]e?|seul(?:e)?)\b",
    r"\bje n['’]en peux plus\b",
    r"\bje ne tiens plus\b",
    r"\bje n['’]arrive (?:plus|pas)\b",
    r"\bje (?:pleure|tremble)\b",
    r"\b(?:submerg|boulevers|d[ée]sesp[ée]r|traumatis|sid[ée]r|insomni|cauchemar)",
    r"\b(?:bloqu|choc|plus envie)",
    r"\b(?:je suis|je me sens) mal\b",
    r"\b(?:a|à) bout\b",
]


EMOTIONAL_SUPPORT_GUIDANCE = {
    "fr": """--- PRIORITE : PERSONNE EN DETRESSE EMOTIONNELLE ---
Le soutien emotionnel passe AVANT le signalement et les conseils techniques, sauf danger immediat.
1. Commence par deux phrases humaines : reconnaitre la souffrance, ne pas culpabiliser et rappeler que la personne n'est pas seule.
2. Aide-la a retrouver un peu de calme avec UNE action simple et immediate (respiration lente ou ancrage), sans lui donner un long exercice.
3. Demande si elle est en securite maintenant seulement si son message montre un effondrement important.
4. Ensuite seulement, donne au maximum deux petites actions pratiques. Les liens de signalement viennent en dernier.
N'inonde pas une personne submergee d'informations, de lois ou de ressources.""",
    "ar": """--- أولوية: شخص في ضائقة عاطفية ---
الدعم النفسي يأتي قبل التبليغ والنصائح التقنية، إلا في حالة الخطر الفوري.
1. ابدأ بجملتين إنسانيتين تعترفان بالألم، بدون لوم، مع التذكير أن الشخص ليس وحده.
2. ساعده على الهدوء بخطوة واحدة بسيطة وفورية مثل التنفس البطيء أو تمرين تثبيت، بدون تمرين طويل.
3. اسأل هل هو في أمان الآن فقط إذا كانت الرسالة تدل على انهيار شديد.
4. بعد ذلك فقط، أعط خطوتين عمليتين قصيرتين كحد أقصى، وضع روابط التبليغ في النهاية.
لا تغرق الشخص المتألم بالمعلومات أو القوانين أو لائحة طويلة من الموارد.""",
}


EMOTIONAL_SUPPORT_OPENERS = {
    "fr": (
        "Je suis désolé que vous traversiez cela. Ce que vous ressentez "
        "compte, ce n'est pas votre faute et vous n'avez pas à l'affronter seul(e)."
    ),
    "ar": (
        "أنا آسف لأنك تمر بهذه المعاناة. إحساسك مهم، وما وقع ليس خطأك، "
        "ولست مضطرا لمواجهة هذا وحدك."
    ),
}


ONLINE_HARM_KEYWORDS = {
    "fr": [
        "harcel", "menac", "chantage", "intimid", "humili", "dox",
        "photo", "video", "contenu", "faux compte", "grooming",
        "prédateur", "predateur", "agress", "diffam", "insult", "usurp",
        "pirat", "sextors", "intime", "publie", "publié", "partage sans",
    ],
    "ar": [
        "تنمر", "تحرش", "تهديد", "يهدد", "ابتزاز", "تخويف", "إهانة",
        "اهانة", "صور", "فيديو", "محتوى", "حساب مزيف", "عنف", "تشهير",
        "سب", "انتحال", "اختراق", "نشر", "شارك",
    ],
}


SOCIAL_MEDIA_KEYWORDS = {
    "fr": [
        "réseau", "reseau", "facebook", "instagram", "tiktok", "whatsapp",
        "telegram", "snapchat", "twitter", "youtube", "plateforme",
        "en ligne", "internet", "compte", "profil", "publication",
        "message", "groupe",
    ],
    "ar": [
        "شبكة", "شبكات", "فيسبوك", "انستغرام", "إنستغرام", "تيك توك",
        "واتساب", "تلغرام", "سناب", "تويتر", "يوتيوب", "منصة",
        "الانترنت", "الإنترنت", "حساب", "بروفايل", "منشور", "رسالة",
        "مجموعة",
    ],
}


IMPLICIT_SOCIAL_MEDIA_HARM_KEYWORDS = {
    "fr": ["cyberharcel", "sextors", "dox", "faux compte"],
    "ar": ["تنمر إلكتروني", "تنمر الكتروني", "ابتزاز إلكتروني", "ابتزاز الكتروني"],
}


SOCIAL_MEDIA_REPORTING_GUIDANCE = {
    "fr": """--- PRIORITE : PROBLEME ACTIF SUR UN RESEAU SOCIAL ---
La reponse doit rester courte et suivre cet ordre :
1. Rassurer la personne sans la culpabiliser.
2. Conserver les preuves, puis signaler le contenu et le compte directement sur le reseau social concerne.
3. Donner obligatoirement ces deux recours exacts :
   - Signalement eVigilance : https://evigilance.ma/fr/signaler
   - Aide EMC/Cyberconfiance : https://www.cyberconfiance.ma
Si un enfant est implique, ajouter ONDE : 2511 et rappeler au parent de ne pas confisquer son appareil.
Ne remplace pas ces liens par des domaines inventes et ne noie pas ces priorites dans une longue liste.""",
    "ar": """--- أولوية: مشكلة قائمة على شبكة اجتماعية ---
يجب أن يكون الجواب قصيرا وبهذا الترتيب:
1. طمأنة الشخص وعدم لومه.
2. حفظ الأدلة، ثم التبليغ عن المحتوى والحساب داخل الشبكة الاجتماعية المعنية.
3. ذكر هاتين الجهتين بالضبط:
   - التبليغ عبر eVigilance: https://evigilance.ma/fr/signaler
   - المساعدة عبر EMC/Cyberconfiance: https://www.cyberconfiance.ma
إذا كان طفل معنيا، أضف مرصد حقوق الطفل ONDE: 2511 وذكّر الوالد بعدم مصادرة جهازه.
لا تستبدل هذه الروابط بروابط مخترعة ولا تضف لائحة طويلة تحجب الأولويات.""",
}


def needs_social_media_reporting(message: str, langue: str = "fr") -> bool:
    """Return whether active social-media harm should prioritize reporting."""
    message_lower = message.lower()
    harm_keywords = ONLINE_HARM_KEYWORDS.get(langue, ONLINE_HARM_KEYWORDS["fr"])
    social_keywords = SOCIAL_MEDIA_KEYWORDS.get(
        langue,
        SOCIAL_MEDIA_KEYWORDS["fr"],
    )
    implicit_keywords = IMPLICIT_SOCIAL_MEDIA_HARM_KEYWORDS.get(
        langue,
        IMPLICIT_SOCIAL_MEDIA_HARM_KEYWORDS["fr"],
    )
    has_implicit_online_harm = any(
        keyword in message_lower for keyword in implicit_keywords
    )
    has_harm = any(keyword in message_lower for keyword in harm_keywords)
    mentions_social_media = any(
        keyword in message_lower for keyword in social_keywords
    )
    return has_implicit_online_harm or (has_harm and mentions_social_media)


def ensure_social_media_reporting(
    answer: str,
    langue: str = "fr",
    include_onde: bool = False,
) -> str:
    """Append omitted reporting actions/resources for social-media harm."""
    missing_resources = []
    answer_lower = answer.lower()
    if langue == "fr":
        mentions_evidence = "preuve" in answer_lower or "capture" in answer_lower
        mentions_platform_report = (
            "signal" in answer_lower
            and any(term in answer_lower for term in ("réseau", "reseau", "plateforme", "compte", "contenu"))
        )
        if not mentions_evidence:
            missing_resources.append("- Conservez les preuves et captures d'écran.")
        if not mentions_platform_report:
            missing_resources.append(
                "- Signalez le contenu et le compte directement sur le réseau social."
            )
    else:
        mentions_evidence = "دليل" in answer or "أدلة" in answer or "الأدلة" in answer
        mentions_platform_report = (
            ("بلغ" in answer or "تبليغ" in answer)
            and any(term in answer for term in ("شبكة", "منصة", "حساب", "محتوى"))
        )
        if not mentions_evidence:
            missing_resources.append("- احتفظ بالأدلة ولقطات الشاشة.")
        if not mentions_platform_report:
            missing_resources.append("- بلّغ عن المحتوى والحساب داخل الشبكة الاجتماعية.")

    if "evigilance.ma/fr/signaler" not in answer.lower():
        missing_resources.append(
            "- eVigilance : https://evigilance.ma/fr/signaler"
        )
    if "cyberconfiance.ma" not in answer.lower():
        missing_resources.append(
            "- EMC/Cyberconfiance : https://www.cyberconfiance.ma"
        )
    if include_onde and "2511" not in answer:
        onde_label = "ONDE (enfant)" if langue == "fr" else "ONDE للأطفال"
        missing_resources.append(f"- {onde_label} : 2511")

    if not missing_resources:
        return answer

    heading = (
        "À faire en priorité — signalement et aide :"
        if langue == "fr"
        else "الأولوية — التبليغ والمساعدة:"
    )
    return f"{answer.rstrip()}\n\n{heading}\n" + "\n".join(missing_resources)


def ensure_emotional_support(answer: str, langue: str = "fr") -> str:
    """Ensure a distressed user receives human support before action steps."""
    opening = answer.lstrip()[:350].lower()
    if langue == "fr":
        support_markers = (
            "désolé", "desole", "je comprends", "pas votre faute",
            "n'est pas votre faute", "pas seul", "soutien", "ressentez",
        )
    else:
        support_markers = (
            "آسف", "أتفهم", "كنفهم", "لست وحد", "ماشي خطأك",
            "ليس خطأك", "إحساس", "شعور",
        )

    if any(marker in opening for marker in support_markers):
        return answer

    opener = EMOTIONAL_SUPPORT_OPENERS.get(
        langue,
        EMOTIONAL_SUPPORT_OPENERS["fr"],
    )
    return f"{opener}\n\n{answer.lstrip()}"


def detect_profile(message: str, langue: str = "fr") -> str:
    """
    Detect the user profile from the message content.
    Returns one of: 'victim', 'parent', 'enseignant', 'temoin', 'jeune',
    'detresse_emotionnelle'.

    Default is 'victim' if no specific profile is detected.
    """
    message_lower = message.lower()

    # Helper for word boundary search
    def _match_keyword(kw: str, text: str) -> bool:
        if re.search(r'[\u0600-\u06FF]', kw):
            # Arabic script: simple substring match or spaced match
            return kw in text
        # Latin script: word boundary check to avoid 'prof' matching 'profil'
        pattern = r'(?<![a-zà-ÿ])' + re.escape(kw) + r'(?![a-zà-ÿ])'
        return bool(re.search(pattern, text))

    # Check emotional distress first (highest priority after urgency).
    if langue == "fr":
        if any(
            re.search(pattern, message_lower)
            for pattern in EMOTIONAL_DISTRESS_PATTERNS_FR
        ):
            return "detresse_emotionnelle"
    else:
        for keyword in PROFILE_KEYWORDS["detresse_emotionnelle"].get(langue, []):
            if keyword.lower() in message_lower:
                return "detresse_emotionnelle"

    # Check other profiles
    for profile in ["parent", "enseignant", "temoin", "jeune"]:
        for keyword in PROFILE_KEYWORDS[profile].get(langue, []):
            if _match_keyword(keyword.lower(), message_lower):
                return profile

    return "victim"


# ============================================================
# System prompts -- loaded from external files
# Files: backend/prompts/system_prompt_fr.txt
#        backend/prompts/system_prompt_ar.txt
# ============================================================

_PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


def _load_prompt(filename: str) -> str:
    """Load a prompt template from backend/prompts/."""
    path = _PROMPTS_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Prompt file not found: {path}")
    return path.read_text(encoding="utf-8")


# Load prompts once at module level
SYSTEM_PROMPT_FR = _load_prompt("system_prompt_fr.txt")
SYSTEM_PROMPT_AR = _load_prompt("system_prompt_ar.txt")
logger.info(f"Loaded prompts: FR={len(SYSTEM_PROMPT_FR)} chars, AR={len(SYSTEM_PROMPT_AR)} chars")

# AR prompt is loaded above from system_prompt_ar.txt


# Latin-script characters, used to tell an Arabizi message apart from an
# Arabic-script one. Mirrors the token alphabet of services/language_service.py.
_LATIN_CHAR_RE = re.compile(r"[a-z\u00e0-\u00f6\u00f8-\u00ff]", re.IGNORECASE)
_ARABIZI_CHAR = r"[0-9a-z\u00e0-\u00f6\u00f8-\u00ff]"

# Arabizi keywords are matched on word boundaries rather than as substrings:
# a short token such as "nmot" must never fire inside an unrelated French
# word. Whitespace inside a multi-word keyword is flexible.
_URGENCY_ARABIZI_RE = re.compile(
    "(?<!" + _ARABIZI_CHAR + ")(?:"
    + "|".join(
        r"\s+".join(re.escape(part) for part in keyword.split())
        for keyword in URGENCY_KEYWORDS_ARABIZI
    )
    + ")(?!" + _ARABIZI_CHAR + ")",
    re.IGNORECASE,
)


def detect_urgency(message: str, langue: str = "fr") -> bool:
    """
    Detect if the user message contains urgency keywords.
    Based on livrable-1 mots_cles_declencheurs.md priority system.

    Three passes, because a Darija speaker may write the same crisis in three
    scripts and language_service routes all Latin-script Darija to "ar":
    1. the keyword list for `langue`;
    2. the French list too, when the message is Latin-script but routed to
       "ar" -- Darija speakers code-switch French constantly;
    3. the Arabizi list, for both pipelines.

    Returns True if any urgency keyword is found.
    """
    message_lower = message.lower()
    keywords = URGENCY_KEYWORDS_FR if langue == "fr" else URGENCY_KEYWORDS_AR

    for keyword in keywords:
        if keyword.lower() in message_lower:
            return True

    if langue != "fr" and _LATIN_CHAR_RE.search(message_lower):
        for keyword in URGENCY_KEYWORDS_FR:
            if keyword.lower() in message_lower:
                return True

    return bool(_URGENCY_ARABIZI_RE.search(message_lower))


class RAGChain:
    """
    Full RAG pipeline with multi-profile support:
    1. Detects user profile (victim, parent, teacher, witness, young)
    2. Checks for urgency keywords (highest priority)
    3. Retrieves relevant documents (retriever)
    4. Builds prompt with context and profile-specific guidance
    5. Sends to Gemini LLM
    6. Returns the response with sources and metadata
    """

    def __init__(
        self,
        model_name: Optional[str] = None,
        temperature: Optional[float] = None,
    ):
        self.retriever = BilingualRetriever()
        self._model_name = model_name
        self._temperature = temperature
        self._provider: Optional[GeminiProvider] = None
        self.conversation_history: List[Dict[str, str]] = []

    @property
    def provider(self) -> GeminiProvider:
        """Initialize Gemini only when a non-urgent message needs it."""
        if self._provider is None:
            self._provider = get_gemini_provider(
                model_name=self._model_name,
                temperature=self._temperature,
            )
        return self._provider

    def get_system_prompt(self, langue: str) -> str:
        """Return the system prompt in the correct language."""
        if langue == "ar":
            return SYSTEM_PROMPT_AR
        return SYSTEM_PROMPT_FR

    def ask(
        self,
        question: str,
        langue: str = "fr",
        include_history: bool = True,
    ) -> dict:
        """
        Ask a question to the RAG pipeline.

        Args:
            question: User question
            langue: "fr" or "ar"
            include_history: Include conversation history

        Returns:
            {
                "answer": str,           # LLM response
                "sources": list,         # Source documents used
                "langue": str,           # Response language
                "context_used": str,     # Injected context
                "is_urgent": bool,       # Whether urgency was detected
                "user_profile": str,     # Detected user profile
            }
        """
        # 0. Detect user profile and urgency
        is_urgent = detect_urgency(question, langue)
        user_profile = detect_profile(question, langue)
        needs_social_reporting = needs_social_media_reporting(question, langue)
        involves_child = user_profile in {"parent", "jeune"}
        needs_emotional_support = user_profile == "detresse_emotionnelle"

        # Safety-critical replies must not wait for retrieval or an external LLM.
        if is_urgent:
            answer = (
                EMERGENCY_RESPONSE_FR if langue == "fr" else EMERGENCY_RESPONSE_AR
            )
            self.conversation_history.append({"role": "user", "content": question})
            self.conversation_history.append({"role": "assistant", "content": answer})
            return {
                "answer": answer,
                "sources": [],
                "langue": langue,
                "context_used": answer,
                "is_urgent": True,
                "user_profile": user_profile,
            }

        # 1. Retrieve relevant documents
        results = self.retriever.search_with_fallback(question, langue=langue)

        # 2. Format context
        context = self.retriever.format_context(results)

        # If urgent, prepend emergency info to context
        if is_urgent:
            emergency_info = (
                EMERGENCY_RESPONSE_FR if langue == "fr" else EMERGENCY_RESPONSE_AR
            )
            context = (
                f"--- URGENCE DETECTEE ---\n{emergency_info}\n\n{context}"
            )

        # Add profile hint to context so the LLM adapts its response
        if user_profile != "victim":
            profile_labels = {
                "parent": "Parent inquiet pour son enfant",
                "enseignant": "Enseignant / Educateur en milieu scolaire",
                "temoin": "Temoin de cyberviolence",
                "jeune": "Jeune / Mineur cherchant information ou aide",
                "detresse_emotionnelle": "Personne en detresse emotionnelle -- activer le soutien psychologique",
            }
            label = profile_labels.get(user_profile, user_profile)
            context = f"--- PROFIL DETECTE : {label} ---\n\n{context}"

        if needs_social_reporting:
            guidance = SOCIAL_MEDIA_REPORTING_GUIDANCE.get(
                langue,
                SOCIAL_MEDIA_REPORTING_GUIDANCE["fr"],
            )
            context = f"{guidance}\n\n{context}"

        # Emotional support takes precedence over reporting/technical guidance.
        if needs_emotional_support:
            guidance = EMOTIONAL_SUPPORT_GUIDANCE.get(
                langue,
                EMOTIONAL_SUPPORT_GUIDANCE["fr"],
            )
            context = f"{guidance}\n\n{context}"

        # 3. Build prompt
        system_prompt = self.get_system_prompt(langue).format(context=context)

        messages = [SystemMessage(content=system_prompt)]

        # Add conversation history (keep last 3 exchanges)
        if include_history:
            for msg in self.conversation_history[-6:]:
                if msg["role"] == "user":
                    messages.append(HumanMessage(content=msg["content"]))
                else:
                    messages.append(AIMessage(content=msg["content"]))

        messages.append(HumanMessage(content=question))

        # 4. Send to Gemini LLM via provider
        answer = self.provider.generate(messages)
        if needs_emotional_support:
            answer = ensure_emotional_support(answer, langue)
        if needs_social_reporting:
            answer = ensure_social_media_reporting(
                answer,
                langue,
                include_onde=involves_child,
            )

        # 5. Update history
        self.conversation_history.append({"role": "user", "content": question})
        self.conversation_history.append({"role": "assistant", "content": answer})

        # 6. Extract sources
        sources = [
            {
                "path": doc.metadata.get("relative_path"),
                "categorie": doc.metadata.get("categorie"),
                "score": round(score, 3),
            }
            for doc, score in results
        ]

        return {
            "answer": answer,
            "sources": sources,
            "langue": langue,
            "context_used": context,
            "is_urgent": is_urgent,
            "user_profile": user_profile,
        }

    def reset_history(self):
        """Reset conversation history."""
        self.conversation_history = []


# === Test the full pipeline ===
if __name__ == "__main__":
    print("Initializing RAG pipeline with Gemini...")
    chain = RAGChain()

    # Test FR -- normal question (victim profile)
    print("\n" + "="*60)
    print("TEST 1: Sextorsion question (victim)")
    print("="*60)
    result = chain.ask("Je suis victime de sextorsion, que dois-je faire ?", langue="fr")
    print(f"Profile: {result['user_profile']}")
    print(f"Urgent: {result['is_urgent']}")
    print(f"Response: {result['answer'][:300]}...")
    chain.reset_history()

    # Test FR -- urgency detection
    print("\n" + "="*60)
    print("TEST 2: Urgency detection")
    print("="*60)
    result = chain.ask("Je suis en danger, il est chez moi", langue="fr")
    print(f"Profile: {result['user_profile']}")
    print(f"Urgent: {result['is_urgent']}")
    print(f"Response: {result['answer'][:300]}...")
    chain.reset_history()

    # Test FR -- parent profile
    print("\n" + "="*60)
    print("TEST 3: Parent inquiet")
    print("="*60)
    result = chain.ask("Mon enfant est victime de cyberharcelement, que dois-je faire ?", langue="fr")
    print(f"Profile: {result['user_profile']}")
    print(f"Response: {result['answer'][:300]}...")
    chain.reset_history()

    # Test FR -- emotional distress
    print("\n" + "="*60)
    print("TEST 4: Detresse emotionnelle")
    print("="*60)
    result = chain.ask("J'ai tellement honte, je suis en panique, je tremble", langue="fr")
    print(f"Profile: {result['user_profile']}")
    print(f"Response: {result['answer'][:300]}...")
    chain.reset_history()

    # Test AR
    print("\n" + "="*60)
    print("TEST 5: Arabic sextorsion")
    print("="*60)
    result = chain.ask(
        "\u0623\u0646\u0627 \u0636\u062d\u064a\u0629 \u0627\u0628\u062a\u0632\u0627\u0632 \u062c\u0646\u0633\u064a\u060c \u0645\u0627\u0630\u0627 \u0623\u0641\u0639\u0644\u061f",
        langue="ar"
    )
    print(f"Profile: {result['user_profile']}")
    print(f"Response: {result['answer'][:300]}...")
