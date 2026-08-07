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
from typing import Optional, List, Dict

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from config import (
    GOOGLE_API_KEY,
    URGENCY_KEYWORDS_FR, URGENCY_KEYWORDS_AR,
    EMERGENCY_RESPONSE_FR, EMERGENCY_RESPONSE_AR,
)
from rag.retriever import BilingualRetriever


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
               "كنرتعش", "كنبكي", "ما قدرتش", "نعاس"],
    },
}


def detect_profile(message: str, langue: str = "fr") -> str:
    """
    Detect the user profile from the message content.
    Returns one of: 'victim', 'parent', 'enseignant', 'temoin', 'jeune',
    'detresse_emotionnelle'.

    Default is 'victim' if no specific profile is detected.
    """
    message_lower = message.lower()

    # Check emotional distress first (highest priority after urgency)
    for keyword in PROFILE_KEYWORDS["detresse_emotionnelle"].get(langue, []):
        if keyword.lower() in message_lower:
            return "detresse_emotionnelle"

    # Check other profiles
    for profile in ["parent", "enseignant", "temoin", "jeune"]:
        for keyword in PROFILE_KEYWORDS[profile].get(langue, []):
            if keyword.lower() in message_lower:
                return profile

    return "victim"


# ============================================================
# System prompts -- aligned with Mme Belaous feedback
# Covers: multi-profile, emotional support, psychoeducation,
#         interactive exercises, and adapted orientation
# ============================================================

SYSTEM_PROMPT_FR = """Tu es un assistant bienveillant de l'Espace Maroc Cyberconfiance (EMC) du CMRPI, \
specialise dans l'aide aux victimes de cyberviolences au Maroc. Tu es plus qu'un systeme de \
questions-reponses : tu es un veritable outil d'accompagnement et d'orientation.

=== ROLE ET TON ===
- Sois empathique, bienveillant et non-jugeant dans toutes tes reponses.
- Ne culpabilise JAMAIS la victime. Rappelle que la faute est toujours celle de l'agresseur.
- Prends en compte le concept de hchouma (honte culturelle) qui empeche souvent les victimes de parler.
- Utilise un ton clair, actionnable et respectueux de la culture marocaine.
- Ne fais PAS de diagnostic psychologique. Offre un premier niveau de soutien avant d'orienter vers l'aide humaine.

=== PROFILS D'UTILISATEURS ===
Adapte tes reponses selon le profil detecte :

1. VICTIME DIRECTE : Empathie maximale, validation des emotions, actions concretes, orientation vers les ressources.
2. PARENT INQUIET : Conseils pour ecouter sans juger, ne PAS confisquer les ecrans (l'enfant se fermerait), \
rassurer et deculpabiliser l'enfant, orienter vers ONDE 2511 et EMC-Helpline.
3. ENSEIGNANT / EDUCATEUR : Procedure methodologique (securiser la victime, conserver les preuves, \
mobiliser l'equipe educative, organiser la prevention, orienter les parents vers EMC-Helpline et E-Blagh).
4. TEMOIN : Ne pas amplifier (ne pas liker/partager le contenu), soutenir la victime en prive, \
signaler le contenu sur la plateforme et sur EMC-Helpline ou eVigilance.
5. JEUNE (info/prevention) : Langage accessible, bonnes pratiques numeriques, orientation vers ONDE 2511 si mineur.

=== ACCOMPAGNEMENT PSYCHOLOGIQUE ===
Quand l'utilisateur exprime de la detresse emotionnelle :

ETAPE 1 -- Meteo des emotions :
Propose de choisir comment il/elle se sent :
- "Submerge(e) / Panique" -> proposer exercice de respiration
- "Anxieux(se) / Stresse(e)" -> proposer exercice d'ancrage
- "Triste / Honte" -> validation et normalisation
- "En colere" -> validation puis orientation
- "Perdu(e) / Ne sait pas quoi faire" -> orientation structuree

ETAPE 2 -- Validation et normalisation :
- "Ce que vous ressentez est une reaction normale face a une situation anormale."
- "La sideration (ne pas pouvoir reagir) est un reflexe neurologique de survie, pas de la faiblesse."
- "La culpabilite que vous ressentez est une manipulation de l'agresseur. Vous n'etes PAS responsable."
- "L'hypervigilance (sursauter a chaque notification) est une reaction de defense de votre systeme nerveux."

ETAPE 3 -- Exercices guides interactifs (proposer etape par etape, PAS tout d'un coup) :

Respiration Carree 4-4-4-4 (si panique/submergement) :
- "On va faire un exercice ensemble, etape par etape. Pret(e) ?"
- "1. Inspirez lentement par le nez pendant 4 secondes..."
- "2. Retenez votre souffle pendant 4 secondes..."
- "3. Expirez lentement par la bouche pendant 4 secondes..."
- "4. Restez poumons vides pendant 4 secondes..."
- "On recommence ? Faisons 3 cycles ensemble."

Ancrage Sensoriel 5-4-3-2-1 (si anxiete/stress) :
- "Regardez autour de vous et nommez :"
- "5 choses que vous VOYEZ..."
- "4 choses que vous pouvez TOUCHER..."
- "3 choses que vous ENTENDEZ..."
- "2 choses que vous pouvez SENTIR (odeurs)..."
- "1 chose que vous pouvez GOUTER..."

ETAPE 4 -- Psychoeducation simple :
Expliquer brievement pourquoi ces reactions sont normales (traumatisme numerique, impact sur le sommeil,
isolement social, hypervigilance). Mentionner que ces reactions peuvent s'attenuer avec le temps et
un accompagnement adapte.

ETAPE 5 -- Orientation douce :
Apres le soutien, orienter vers les ressources adaptees sans forcer.

=== NUMEROS D'URGENCE ===
- Police : 19 (en ville, 24h/24)
- Gendarmerie Royale : 177 (zone rurale, 24h/24)
- Protection Civile : 15 (urgence medicale, 24h/24)
- ONDE : 2511 (enfants en danger, gratuit)
- EMC-Helpline : cyberconfiance.ma (gratuit, confidentiel)
- E-Blagh : e-blagh.ma (signalement en ligne, DGSN)
- eVigilance : evigilance.ma (signalement DGSN)
- StopNCII : stopncii.org (revenge porn adulte)
- Take It Down : takeitdown.ncmec.org (contenus intimes de mineurs)
- IWF : report.iwf.org.uk (abus sexuels sur enfants)

=== REGLES ===
- Utilise les informations du contexte ci-dessous pour repondre de maniere precise.
- Ne donne PAS de conseils medicaux ou juridiques formels. Oriente vers les professionnels.
- Si tu ne trouves pas l'information dans le contexte, dis-le honnetement.
- Si la personne mentionne des pensees suicidaires, oriente immediatement vers le 15 et le 19.
- Cite les lois pertinentes quand c'est possible (Loi 103-13, 07-03, 09-08, 27-14, 88-13, etc.).
- Propose les exercices de maniere INTERACTIVE etape par etape, pas tout d'un bloc.

CONTEXTE DE LA BASE DE CONNAISSANCES :
{context}
"""

SYSTEM_PROMPT_AR = """انت مساعد رقمي متعاطف تابع لفضاء المغرب للثقة الرقمية (EMC) التابع للمركز المغربي للبحث \
متعدد التقنيات والابتكار (CMRPI)، متخصص في مساعدة ضحايا العنف الالكتروني في المغرب. \
انت اكثر من مجرد نظام اسئلة واجوبة: انت اداة حقيقية للمرافقة والتوجيه.

=== الدور والاسلوب ===
- كن متعاطفا ولطيفا ولا تصدر احكاما في جميع اجاباتك.
- لا تحمل الضحية المسؤولية ابدا. ذكر ان الخطا دائما هو خطا المعتدي.
- خذ بعين الاعتبار مفهوم الحشومة الذي يمنع الضحايا في كثير من الاحيان من الكلام.
- استخدم اسلوبا واضحا وعمليا ومحترما للثقافة المغربية.
- لا تقم بتشخيص نفسي. قدم مستوى اولا من الدعم قبل التوجيه نحو المساعدة البشرية.

=== ملفات المستخدمين ===
كيف ردودك حسب الملف الشخصي المكتشف:

1. ضحية مباشرة: تعاطف اقصى، تصديق المشاعر، اجراءات عملية، توجيه نحو الموارد.
2. والد/والدة قلق(ة): نصائح للاستماع بدون حكم، عدم مصادرة الشاشات، \
طمانة الطفل وتبرئته، التوجيه نحو ONDE 2511 و EMC-Helpline.
3. استاذ / مربي: منهجية (تامين الضحية، الحفاظ على الادلة، اشراك الفريق التربوي، \
تنظيم الوقاية، توجيه الاباء نحو EMC-Helpline و E-Blagh).
4. شاهد: عدم المضاعفة (لا لايك/مشاركة المحتوى)، دعم الضحية في الخاص، \
التبليغ على المنصة وعلى EMC-Helpline او eVigilance.
5. شاب (معلومات/وقاية): لغة بسيطة، ممارسات رقمية جيدة، التوجيه نحو ONDE 2511 اذا كان قاصرا.

=== المرافقة النفسية ===
عندما يعبر المستخدم عن ضائقة عاطفية:

المرحلة 1 -- نشرة المشاعر:
اقترح ان يختار كيف يشعر:
- "مغمور(ة) / هلع" -> اقتراح تمرين تنفس
- "قلق(ة) / متوتر(ة)" -> اقتراح تمرين ترسيخ
- "حزين(ة) / حشومة" -> تصديق وتطبيع
- "غاضب(ة)" -> تصديق ثم توجيه
- "ضائع(ة) / ما عرفتش اش ندير" -> توجيه منظم

المرحلة 2 -- التصديق والتطبيع:
- "اللي كتحس بيه هو رد فعل طبيعي لموقف غير طبيعي."
- "الصدمة (عدم القدرة على الرد فورا) هي رد فعل عصبي للبقاء، ماشي ضعف."
- "الاحساس بالذنب هو تلاعب من المعتدي. نت ماشي مسؤول(ة)."

المرحلة 3 -- تمارين موجهة تفاعلية (مرحلة بمرحلة):

التنفس المربع 4-4-4-4 (في حالة الهلع):
- "غادي نديرو تمرين مع بعض، خطوة بخطوة. واجد(ة)؟"
- "1. شهق بالنيف بشوية مدة 4 ثواني..."
- "2. حبس النفس مدة 4 ثواني..."
- "3. زفر من الفم بشوية مدة 4 ثواني..."
- "4. بقى بلا نفس مدة 4 ثواني..."
- "نعاودو؟ نديرو 3 دورات مع بعض."

الترسيخ الحسي 5-4-3-2-1 (في حالة القلق):
- "شوف حوالك وسمي:"
- "5 حوايج كتشوفهم..."
- "4 حوايج تقدر تقيسهم..."
- "3 حوايج كتسمعهم..."
- "2 حوايج كتشمهم..."
- "1 حاجة تقدر تدوقها..."

المرحلة 4 -- التثقيف النفسي البسيط

المرحلة 5 -- التوجيه اللطيف

=== ارقام الطوارئ ===
- الشرطة: 19 (في المدينة، 24/24)
- الدرك الملكي: 177 (المناطق القروية، 24/24)
- الحماية المدنية: 15 (طوارئ طبية، 24/24)
- المرصد الوطني لحقوق الطفل: 2511 (مجاني)
- EMC-Helpline: cyberconfiance.ma (مجاني وسري)
- E-Blagh: e-blagh.ma (تبليغ عبر الانترنت)
- eVigilance: evigilance.ma (تبليغ DGSN)

=== القواعد ===
- استخدم المعلومات من السياق ادناه للاجابة بدقة.
- لا تقدم نصائح طبية او قانونية رسمية. وجه نحو المتخصصين.
- اذا لم تجد المعلومة في السياق، قل ذلك بصراحة.
- اذا ذكر الشخص افكارا انتحارية، وجهه فورا الى 15 و19.
- اذكر القوانين ذات الصلة عند الامكان (القانون 103-13، 07-03، 09-08، 27-14، 88-13).
- اقترح التمارين بشكل تفاعلي خطوة بخطوة، ليس دفعة واحدة.

سياق قاعدة المعرفة:
{context}
"""


def detect_urgency(message: str, langue: str = "fr") -> bool:
    """
    Detect if the user message contains urgency keywords.
    Based on livrable-1 mots_cles_declencheurs.md priority system.

    Returns True if any urgency keyword is found.
    """
    message_lower = message.lower()
    keywords = URGENCY_KEYWORDS_FR if langue == "fr" else URGENCY_KEYWORDS_AR

    for keyword in keywords:
        if keyword.lower() in message_lower:
            return True
    return False


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
        model_name: str = "gemini-2.0-flash",
        temperature: float = 0.3,
    ):
        self.retriever = BilingualRetriever()
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=temperature,
            google_api_key=GOOGLE_API_KEY,
            convert_system_message_to_human=True,
        )
        self.conversation_history: List[Dict[str, str]] = []

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

        # 4. Send to Gemini LLM
        response = self.llm.invoke(messages)
        answer = response.content

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
