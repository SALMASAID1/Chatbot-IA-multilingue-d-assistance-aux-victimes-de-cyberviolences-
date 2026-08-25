"""Centralized configuration for the RAG pipeline."""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# Paths
# ============================================================
PROJECT_ROOT = Path(__file__).parent.parent  # project root
KNOWLEDGE_BASE_DIR = PROJECT_ROOT / "data" / "knowledge_base"
FR_DIR = KNOWLEDGE_BASE_DIR / "fr"
AR_DIR = KNOWLEDGE_BASE_DIR / "ar"
FR_METADATA = FR_DIR / "metadata.json"
AR_METADATA = AR_DIR / "metadata.json"
CHROMA_PERSIST_DIR = PROJECT_ROOT / "data" / "chroma_db"

# Livrable-1 Q&A bases (additional ingestion sources)
LIVRABLE_1_DIR = PROJECT_ROOT / "docs" / "livrable-1"
QR_FR_PATH = LIVRABLE_1_DIR / "base_questions_reponses_fr.md"
QR_AR_PATH = LIVRABLE_1_DIR / "base_questions_reponses_ar.md"
MOTS_CLES_PATH = LIVRABLE_1_DIR / "mots_cles_declencheurs.md"

# Directories to exclude from ingestion (duplicates)
EXCLUDED_DIRS = ["cyberviolence_ressources_verified_md"]

# ============================================================
# Chunking parameters
# ============================================================
CHUNK_SIZE = 500          # in characters (~100-125 tokens)
CHUNK_OVERLAP = 50        # overlap between chunks

# ============================================================
# Embedding model
# ============================================================
# Multilingual FR/AR -- good balance between performance and size
EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
)
# auto: prefer a complete local Hugging Face snapshot, otherwise download it.
# true: require a local snapshot. false: always resolve through Hugging Face.
EMBEDDING_LOCAL_FILES_ONLY = os.getenv(
    "EMBEDDING_LOCAL_FILES_ONLY", "auto"
).strip().lower()
# Alternative, more accurate but heavier:
# EMBEDDING_MODEL = "intfloat/multilingual-e5-large"

# ============================================================
# Retriever parameters
# ============================================================
TOP_K = int(os.getenv("TOP_K", "3"))
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.15"))

# ============================================================
# API Keys
# ============================================================
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
GEMINI_FALLBACK_MODELS = [
    model.strip()
    for model in os.getenv(
        "GEMINI_FALLBACK_MODELS",
        "gemini-3.1-flash-lite,gemini-3.6-flash",
    ).split(",")
    if model.strip()
]
GEMINI_MAX_OUTPUT_TOKENS = int(os.getenv("GEMINI_MAX_OUTPUT_TOKENS", "300"))
GEMINI_REQUEST_TIMEOUT_SECONDS = float(
    os.getenv("GEMINI_REQUEST_TIMEOUT_SECONDS", "20")
)
GEMINI_MAX_RETRIES = int(os.getenv("GEMINI_MAX_RETRIES", "1"))
GEMINI_THINKING_LEVEL = os.getenv("GEMINI_THINKING_LEVEL", "minimal")

# ============================================================
# API Configuration
# ============================================================
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
API_VERSION = "1.0.0"
CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS", "http://localhost:5173,http://localhost:3000"
).split(",")

# ============================================================
# Session configuration
# ============================================================
SESSION_TTL_MINUTES = int(os.getenv("SESSION_TTL_MINUTES", "30"))
MAX_HISTORY_SIZE = int(os.getenv("MAX_HISTORY_SIZE", "50"))
MAX_MESSAGE_LENGTH = int(os.getenv("MAX_MESSAGE_LENGTH", "2000"))

# ============================================================
# Admin authentication
# ============================================================
# When unset, the /api/admin/* endpoints are disabled entirely (they answer 404).
# Set it to a long random value to enable them, e.g.:
#   python -c "import secrets; print(secrets.token_urlsafe(32))"
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY") or None

# ============================================================
# Rate limiting
# ============================================================
RATE_LIMIT_CHAT = os.getenv("RATE_LIMIT_CHAT", "30/minute")
RATE_LIMIT_ADMIN = os.getenv("RATE_LIMIT_ADMIN", "10/minute")

# ============================================================
# Redis (optional, for production sessions)
# ============================================================
REDIS_URL = os.getenv("REDIS_URL", None)

# ============================================================
# ChromaDB collection
# ============================================================
CHROMA_COLLECTION_NAME = "cyberviolence_knowledge"

# ============================================================
# Urgency keywords (from livrable-1 mots_cles_declencheurs.md)
# These trigger emergency protocol -- always highest priority
# ============================================================
URGENCY_KEYWORDS_FR = [
    "danger", "en danger", "urgence", "urgent", "aide immediate",
    "menace physiquement", "il est chez moi", "il va me frapper",
    "suicide", "me tuer", "en finir", "finir avec la vie",
    "plus envie de vivre", "plus la force", "me faire du mal",
    "envie de mourir", "mourir", "automutilation", "danger immediat",
]

URGENCY_KEYWORDS_AR = [
    "خطر", "ف خطر", "طوارئ", "مهدد", "غادي يضربني", "راه عند الباب",
    "انتحار", "بغيت نموت", "ماعندي مع الحياة", "نقتل راسي",
    "ما بقات عندي القوة",
]

# Latin-script Darija (Arabizi). Neither list above reaches it: the Arabic
# list is Arabic-script only, and a Latin-script message is routed to the
# Arabic pipeline as soon as language_service finds one Darija marker. Before
# this list, "bghit nmot" was NOT flagged as urgent while its Arabic-script
# spelling "بغيت نموت" was.
#
# Arabizi has no standard orthography, so common spelling variants are listed
# explicitly (digits stand for Arabic letters: 3=ع, 7=ح, 9=ق). These entries are
# matched on word boundaries -- never as substrings -- so a short token such
# as "nmot" cannot fire inside an unrelated French word.
URGENCY_KEYWORDS_ARABIZI = [
    # Suicidal ideation / self-harm ("bghit nmot", "nqtel rasi")
    "nmot", "nmout", "nmut",
    "nqtel rasi", "n9tel rasi", "nktel rasi",
    "nqtel rassi", "n9tel rassi", "nktel rassi",
    "nsali 7yati", "nsali hyati", "nsali m3a 7yati", "nsali m3a hyati",
    "3yit men 7yati", "3yit mn 7yati", "3ayit men 7yati", "3ayit mn 7yati",
    # No strength left -- parity with the FR "plus la force"
    "ma bqach 3andi la9wa", "ma b9ach 3andi la9wa",
    "mabqach 3andi la9wa", "mab9ach 3andi la9wa",
    "ma bqach 3andi laqwa", "ma bqatch la9wa",
    # Immediate physical danger -- parity with the AR list
    "f khatar", "fkhatar", "f khtar", "f lkhatar",
    "ghadi ydrebni", "ghadi idrebni", "ghadi ydribni",
    "ghadi yqtelni", "ghadi y9telni", "ghadi yktelni",
    "rah 3end bab", "rah 3and bab",
]

EMERGENCY_RESPONSE_FR = (
    "Si vous etes en danger immediat, appelez les autorites tout de suite :\n"
    "- Police : 19 (en ville)\n"
    "- Gendarmerie Royale : 177 (en zone rurale)\n"
    "- Protection Civile : 15 (urgence medicale)\n"
    "- ONDE : 2511 (si la victime est un enfant)\n"
    "- EMC-Helpline : cyberconfiance.ma (en ligne, gratuit)\n"
    "\nVous n'etes pas seul(e). L'aide est disponible 24h/24."
)

EMERGENCY_RESPONSE_AR = (
    "اذا كنت في خطر فوري، اتصل بالسلطات فورا:\n"
    "- الشرطة: 19 (في المدينة)\n"
    "- الدرك الملكي: 177 (في المناطق القروية)\n"
    "- الحماية المدنية: 15 (طوارئ طبية)\n"
    "- المرصد الوطني لحقوق الطفل: 2511\n"
    "- EMC-Helpline: cyberconfiance.ma (مجاني)\n"
    "\nلست وحدك. المساعدة متاحة 24/24."
)
