# Workspace Analysis — EMC Helpline Chatbot

**Repository:** `Chatbot-IA-multilingue-d-assistance-aux-victimes-de-cyberviolences-`
**Analysed:** 2026-08-24 · branch `salma` @ `f8ca6b0` · working tree clean
**Verified by:** full source read + `pytest` run + live ChromaDB/OpenAPI inspection

---

## 1. What this project is

A multilingual (French / Modern Standard Arabic / Moroccan Darija) RAG chatbot that assists victims of
cyberviolence in Morocco. It is a PFA (end-of-studies project) built for **CMRPI — Espace Maroc
Cyberconfiance (EMC)** by Salma Said and Mohamed Tamzirt, supervised by M. Anass Bentaleb (AI) and
Mme Fadwa Belaous (psychology). Timeline per [project_guide.md](project_guide.md): 1 July – 30 August 2026, four 2-week sprints.

The product is not a generic Q&A bot. Its domain logic encodes three things that matter more than
retrieval quality:

1. **Crisis safety** — messages containing danger/suicide keywords bypass retrieval and the LLM entirely
   and return hard-coded Moroccan emergency numbers.
2. **Persona adaptation** — five user profiles (victim, parent, teacher, witness, youth) plus an
   emotional-distress path, each steering the system prompt differently.
3. **Cultural framing** — explicit handling of *hchouma* (shame), zero victim-blaming, and Darija
   in both Arabic script and Arabizi (Latin transliteration).

**Current state:** backend is complete and tested (Sprints 1–2 done). **No frontend exists yet** —
Sprint 3 (React UI) has not been started. There is no deployed instance.

---

## 2. Repository layout

```
.
├── backend/                    # FastAPI app + RAG pipeline (the entire codebase, ~4.6k LOC)
│   ├── main.py                 # ASGI entry point, lifespan warmup, router wiring
│   ├── config.py               # Single source of truth for all settings + urgency constants
│   ├── demo_cli.py             # Terminal demo (interactive + --auto presentation mode)
│   ├── Dockerfile
│   ├── api/
│   │   ├── models/schemas.py   # All Pydantic request/response models
│   │   ├── routes/             # chat.py · health.py · admin.py
│   │   └── middleware/         # cors.py · rate_limit.py (slowapi)
│   ├── llm/gemini_provider.py  # Gemini wrapper w/ multi-model fallback
│   ├── prompts/                # system_prompt_fr.txt · system_prompt_ar.txt (externalised)
│   ├── rag/                    # ingestion.py · embeddings.py · retriever.py · chain.py
│   ├── services/               # language_service · session_service · chat_service
│   └── tests/, rag/tests/      # 167 tests
├── data/
│   ├── knowledge_base/fr|ar/   # 33 FR + 24 AR curated Markdown docs + metadata.json
│   └── chroma_db/              # Persisted vector store (gitignored, 6.1 MB, 748 vectors)
├── docs/                       # Deliverables: analysis, scenarios, Q&A bases, LLM evaluation
│   ├── livrable-1/             # 32 FR + 32 AR validated Q&A pairs, trigger-keyword matrix
│   └── resources/              # Source PDFs from EMC/CMRPI
├── plan/sprint1..4/            # 13 task files with ownership + status
├── docker-compose.yml          # api + redis services
├── requirements.txt
└── .env / .env.example
```

**Languages:** 35 Python files (~4,589 LOC incl. tests), 85 Markdown files. No JS/TS anywhere.

---

## 3. Architecture

### Request flow

```
HTTP POST /api/chat
  │
  ├─ slowapi rate limit (30/min per IP)  →  429 on excess
  │
  ▼
chat.py::send_message
  │  offloads to a worker thread (asyncio.to_thread) — the pipeline is fully synchronous
  ▼
ChatService.process_message                     (services/chat_service.py)
  ├─ 1. detect_language(message)                (services/language_service.py)
  │      script-first heuristic → "fr" | "ar" + is_darija flag
  ├─ 2. get-or-create Session                   (services/session_service.py)
  │      each Session lazily owns its own RAGChain
  ▼
RAGChain.ask(question, langue)                  (rag/chain.py)
  ├─ detect_urgency  ──► TRUE ──► return hard-coded emergency text  (no retrieval, no LLM)
  ├─ detect_profile        → victim | parent | enseignant | temoin | jeune | detresse_emotionnelle
  ├─ needs_social_media_reporting → bool
  ├─ BilingualRetriever.search_with_fallback    (rag/retriever.py)
  │      Chroma similarity search filtered by langue, k=max(4·top_k,12)
  │      + lexical rerank on metadata/keywords, threshold 0.15, cross-lingual fallback
  ├─ context assembly: [emotional guidance] + [social-media guidance] + [profile label] + docs
  ├─ system prompt (FR or AR) .format(context=…) + last 3 exchanges + user message
  ├─ GeminiProvider.generate(messages)          (llm/gemini_provider.py)
  │      tries GEMINI_MODEL, then each GEMINI_FALLBACK_MODELS on 429/404/503/504
  └─ post-processing guardrails:
         ensure_emotional_support() — prepends a human opener if the model skipped it
         ensure_social_media_reporting() — appends evidence/report steps + eVigilance,
                                           Cyberconfiance, ONDE 2511 links if omitted
  ▼
ChatResponse { answer, sources[], langue, is_darija, is_urgent, user_profile,
               session_id, message_id, timestamp }
```

### Design decisions worth noting

| Decision | Where | Rationale visible in code |
|---|---|---|
| Urgency short-circuits the LLM | [chain.py:433](backend/rag/chain.py#L433) | "Safety-critical replies must not wait for retrieval or an external LLM" |
| Prompts as external `.txt` files | [prompts/](backend/prompts/) | Non-developers (psychologist supervisor) can edit them without touching code |
| Provider abstraction over Gemini | [gemini_provider.py](backend/llm/gemini_provider.py) | Swap LLMs without touching the chain |
| Post-hoc answer repair | [chain.py:154-238](backend/rag/chain.py#L154-L238) | Deterministic guarantee that reporting links/support openers appear, regardless of LLM output |
| Per-session `RAGChain` | [session_service.py:41](backend/services/session_service.py#L41) | Independent conversation history per user |
| Startup warmup | [main.py:44-80](backend/main.py#L44-L80) | Embedding model + vector store + Gemini client loaded before first request |
| Deterministic language detection | [language_service.py](backend/services/language_service.py) | Arabic script ⇒ `ar`; Latin defaults to `fr` unless a *complete* Arabizi word matches — deliberately avoids substring false-positives ("fin", "profil") |

---

## 4. API surface

Verified against the generated OpenAPI schema:

| Method | Path | Summary | Rate limit |
|---|---|---|---|
| `GET` | `/api/health` | API + RAG + LLM status, uptime, active sessions | none |
| `POST` | `/api/chat` | Send message, get RAG answer | 30/min |
| `POST` | `/api/chat/session` | Create a session | none |
| `GET` | `/api/chat/history/{session_id}` | Full conversation history | none |
| `POST` | `/api/chat/feedback` | Rating 1–5 + optional comment | none |
| `GET` | `/api/admin/sessions` | List active sessions + language breakdown | 10/min |
| `DELETE` | `/api/admin/sessions/{session_id}` | Force-expire a session | 10/min |

`/` redirects to `/docs`; Swagger and ReDoc are both enabled.

**Health semantics:** `status` is `healthy` only when `rag_status == "healthy"` **and**
`llm_status ∈ {configured, healthy}`; otherwise `degraded`. `rag_status` can be
`healthy | empty | not_initialized | requires_model_download | error` — a genuinely useful
distinction that avoids a network call.

---

## 5. Data layer

### Knowledge base (`data/knowledge_base/`)

| | FR | AR |
|---|---|---|
| Markdown files ingested | 33 | 24 |
| `metadata.json` entries | 33 | 24 |
| Categories | juridique 6, fiches_pratiques 9, prevention 6, rapports_internationaux 4, psychologie 3, ressources 3, faq 2 | fiches_pratiques 6, prevention 4, rapports_internationaux 4, juridique 3, psychologie 3, ressources 3, faq 1 |

Six additional files under `fr/ressources/cyberviolence_ressources_verified_md/` are deliberately
excluded as duplicates via `EXCLUDED_DIRS` ([config.py:22](backend/config.py#L22)).

Legal coverage is Morocco-specific: laws **103-13** (violence against women), **07-03** (cybercrime),
**09-08** (personal data), **27-14** (trafficking / penal art. 503), **88-13** (press & publishing).

### Additional ingestion source (`docs/livrable-1/`)

32 FR + 32 AR validated Q&A pairs, split per-question by regex on `### Q<n>` / `### س<n>`
([ingestion.py:107](backend/rag/ingestion.py#L107)), plus the trigger-keyword matrix as one reference doc.

### Vector store (live inspection)

| Metric | Value |
|---|---|
| Collection | `cyberviolence_knowledge` |
| Vectors | **748** |
| By language | fr **535** · ar **213** |
| By category | juridique 123, ressources 120, psychologie 119, fiches_pratiques 101, prevention 85, rapports_internationaux 74, faq 66, mots_cles 42, soutien_psychologique 10, profils_utilisateurs 8 |
| By doc type | plain KB 593 · qa_pair 113 · reference 42 |
| Embedding model | `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (384-dim, CPU, normalised) |
| Chunking | 500 chars / 50 overlap, Markdown-aware separators |
| Store size | 6.1 MB on disk (gitignored) |

Ingestion is idempotent: chunk IDs are SHA-256 of `(index, langue, relative_path, content)` and the
collection is reset by default ([embeddings.py:113-124](backend/rag/embeddings.py#L113-L124)).

---

## 6. Safety and domain logic

This is the most distinctive part of the codebase and lives mostly in [config.py](backend/config.py) and [chain.py](backend/rag/chain.py).

- **Urgency keywords** — 19 FR + 11 AR phrases covering immediate physical danger and suicidal
  ideation. A match returns a fixed response listing Police 19, Gendarmerie Royale 177, Protection
  Civile 15, ONDE 2511, EMC-Helpline. No LLM involvement, so no latency and no generation risk.
- **Profile detection** — keyword sets per profile, with Latin-script matching guarded by word
  boundaries (so `prof` never matches `profil`) and Arabic matched by substring. Emotional distress is
  checked first and, in French, via 16 regex patterns rather than plain keywords.
- **Emotional-support precedence** — when distress is detected, guidance injected into the context
  explicitly orders support *before* reporting/legal content, unless there is immediate danger.
- **Social-media reporting** — if the message describes active online harm on a platform, the chain
  both instructs the model and then *verifies the output*, appending eVigilance / Cyberconfiance /
  ONDE links and evidence-preservation steps if the model omitted them.
- **Anti-hallucination on URLs** — both system prompts forbid inventing URLs; the guardrail appends
  the canonical links rather than trusting generation.

The system prompts themselves (FR ~180 lines, AR ~90 lines) encode: 120-word answer cap, max 3 bullet
actions, the "météo des émotions" triage, the 4-4-4-4 square-breathing and 5-4-3-2-1 grounding
exercises delivered step-by-step, psychoeducation on freeze/hypervigilance, and the full emergency
directory.

---

## 7. Configuration

All settings flow through [backend/config.py](backend/config.py) with `.env` overrides. `.env` and `.env.example` currently
declare an identical key set.

| Variable | Default | Notes |
|---|---|---|
| `GOOGLE_API_KEY` | — | Required; present locally |
| `GEMINI_MODEL` | `gemini-3.5-flash-lite` | |
| `GEMINI_FALLBACK_MODELS` | `gemini-3.1-flash-lite,gemini-3.6-flash` | Tried in order on quota/404/503/504 |
| `GEMINI_MAX_OUTPUT_TOKENS` | 300 | Enforces the short-answer policy |
| `GEMINI_REQUEST_TIMEOUT_SECONDS` / `GEMINI_MAX_RETRIES` / `GEMINI_THINKING_LEVEL` | 20 / 1 / `minimal` | Tuned for latency |
| `EMBEDDING_LOCAL_FILES_ONLY` | `auto` | `auto` prefers the local HF snapshot, falls back to download |
| `TOP_K` / `SIMILARITY_THRESHOLD` | 3 / 0.15 | |
| `SESSION_TTL_MINUTES` / `MAX_HISTORY_SIZE` / `MAX_MESSAGE_LENGTH` | 30 / 50 / 2000 | |
| `RATE_LIMIT_CHAT` / `RATE_LIMIT_ADMIN` | 30/minute / 10/minute | |
| `CORS_ORIGINS` | `localhost:5173,localhost:3000` | Vite + CRA dev ports |
| `REDIS_URL` | unset | **Declared but never read by any code** |
| `RUN_LIVE_LLM_TESTS` | 0 | Gates 7 quota-spending tests |

---

## 8. Tests — actual results

Run: `venv/bin/python -m pytest backend -q` (Python 3.11.9)

```
160 passed, 7 skipped, 1 warning in 8.62s      (167 collected)
```

| Suite | Result | Coverage |
|---|---|---|
| `backend/tests/` | 99 passed | Chat routes (mocked RAG), language detection, schemas, session lifecycle, response quality |
| `backend/rag/tests/` | 61 passed, 7 skipped | Ingestion, retriever (against the real vector store), chain/urgency/profile detection |

The 7 skips are the live-Gemini tests, gated behind `RUN_LIVE_LLM_TESTS=1` so a normal run does not
spend API quota — a deliberate and well-labelled choice ([test_chain.py:275](backend/rag/tests/test_chain.py#L275)).

The only warning is a Starlette deprecation notice about `httpx` in `TestClient` — third-party, harmless.

Live status at time of analysis: `rag_status = healthy`, `llm_status = configured`.

---

## 9. Deployment

- **[backend/Dockerfile](backend/Dockerfile)** — `python:3.11-slim`, gcc for native builds, requirements layer cached
  before source copy, `HEALTHCHECK` hitting `/api/health`, `CMD uvicorn backend.main:app`.
- **[docker-compose.yml](docker-compose.yml)** — `api` (port 8000, `.env` file, `./data` bind-mounted so the vector
  store and KB persist) + `redis:7-alpine` with a named volume. Both `restart: unless-stopped`.
- The image is not published anywhere and there is no CI configuration, no `.dockerignore`, and no
  deployment target configured.

---

## 10. Project management state

Sprint files under [plan/](plan/) carry explicit ownership and status:

| Sprint | Tasks | Status |
|---|---|---|
| 1 — Analysis & knowledge base | 4 tasks | ✅ All marked TERMINÉE; deliverables exist in `docs/` |
| 2 — AI engine & backend | RAG (Salma), FastAPI (Mohamed), LLM+prompts (both) | Code complete and tested; only task3 is explicitly marked TERMINÉE in its file |
| 3 — Interface & multilingual | React UI, translation module, E2E | ⬜ Not started — no `frontend/` directory exists |
| 4 — Tests & documentation | Test campaign, deployment, final report | ⬜ Partially anticipated by the existing test suite |

**Branches:** `main`, `mohamed`, and `origin/*` all sit at `1ed9f4a`. `salma` (current, and the branch
with the most recent RAG work) is **1 commit ahead of `main`** and matches `origin/salma`. Nothing is
uncommitted. The RAG-quality commit `f8ca6b0` has not been merged into `main`.

---

## 11. Observations, gaps, and risks

Ordered roughly by impact. Everything here was verified against the source.

### Blocking for the project plan
1. **No frontend.** Sprint 3's React interface — including RTL support for Arabic, the largest
   remaining user-facing deliverable — does not exist. CORS is already configured for Vite's port,
   so the backend is ready for it.
2. **Sprint 2 work is stranded on `salma`.** `f8ca6b0` (improved embeddings handling, language
   detection, response quality) is not in `main`.

### Correctness / dead code
3. **Unreachable urgency branch.** [chain.py:455-461](backend/rag/chain.py#L455-L461) prepends emergency info to the retrieval
   context when `is_urgent` — but `is_urgent` already returned at line 433, so this block can never
   execute. Harmless, but it misleads anyone reading the flow.
4. **`MAX_MESSAGE_LENGTH` is dead config.** Defined at [config.py:91](backend/config.py#L91), never imported; the real limit is
   hard-coded as `max_length=2000` at [schemas.py:33](backend/api/models/schemas.py#L33). Changing the env var silently does nothing.
5. **`REDIS_URL` is dead config.** `redis` is in `requirements.txt` and a Redis service runs in
   `docker-compose.yml`, but no code reads `REDIS_URL` and no `RedisSessionStore` exists — the
   `SessionStore` ABC anticipates it, but only `InMemorySessionStore` is implemented. Sessions are
   lost on restart and are not shared across workers.
6. **Stale docstring.** [language_service.py:66](backend/services/language_service.py#L66) documents `raw_detection` as "raw langdetect output",
   but `langdetect` is neither used nor a dependency — detection is a hand-written heuristic.
7. **`datetime.utcnow()` used in 13 places.** Deprecated from Python 3.12; the project pins 3.11 in
   Docker so nothing breaks today, but an upgrade will emit warnings throughout.

### Production readiness
8. **Admin endpoints are unauthenticated.** `GET /api/admin/sessions` exposes session IDs, timestamps
   and message counts, and `DELETE` destroys sessions — with no auth dependency anywhere in the
   codebase (no `Depends`, no API-key header). Rate limiting is the only barrier. For a service
   handling cyberviolence victims, this is the most serious deployment risk.
9. **Rate limiting is per-process and in-memory.** slowapi's default storage means limits reset on
   restart and are not shared across replicas.
10. **Single-process state.** Sessions, rate limits, and per-session `RAGChain` objects all live in
    process memory, so the API cannot be scaled horizontally as written.
11. **No `.dockerignore`.** The build context is the repo root, so `venv/` (hundreds of MB), `.git/`,
    and `data/chroma_db/` are all sent to the daemon and `COPY . .`'d into the image.
12. **Vector store is gitignored.** A fresh clone has no `data/chroma_db/`; `python -m backend.rag.embeddings`
    must be run before the API reports healthy. This is correct hygiene but is not documented anywhere
    a newcomer would find it — there is no README at the repo root.
13. **Duplicated conversation history.** History is kept both in `Session.history` and in
    `RAGChain.conversation_history`, updated independently. They cannot currently diverge in a
    user-visible way, but the duplication invites drift.

### Content / documentation drift
14. **Model naming inconsistency.** [docs/evaluation_llm.md](docs/evaluation_llm.md) and [plan/sprint2/task3.md](plan/sprint2/task3.md) both state
    the model is **Gemini 2.5 Flash**, and [demo_cli.py](backend/demo_cli.py) prints "Gemini 2.5 Flash" on screen — but the
    configured model is `gemini-3.5-flash-lite` with `gemini-3.1-flash-lite` / `gemini-3.6-flash`
    fallbacks. The evaluation report's numbers were produced against a different model than the one
    that now runs.
15. **Counts drift across docs.** `livrable-1/README.md` says 28 Q&A pairs per language; the files
    contain 32 each. Sprint 1 task files say 23 KB documents per language; the FR base now has 33.
16. **`project_guide.md` links to files that don't exist** — `docs/rapport_projet.tex` and
    `docs/rapport_projet.pdf` are referenced as generated deliverables but are absent.
17. **Arabic index is 2.5× thinner than French** (213 vs 535 vectors), reflecting 24 vs 33 source
    documents. Since Darija routes to the Arabic pipeline, Darija users hit the sparser index. The
    cross-lingual fallback in `search_with_fallback` mitigates but does not fix this.
18. **A stray file literally named `'`** (a single quote) is tracked in git at the repo root, empty —
    the residue of an unterminated shell quote.
19. **`demo_cli.py` scenario labels are mismatched** — scenario 1 is titled "Victime de Sextorsion
    (Français)" but sends Arabizi Darija (`ana ma9hora o knbki chno nder?`), and scenario 3 is titled
    "Détection de Situation d'Urgence" but sends a sextortion threat that will not trigger the urgency
    path. Worth fixing before a supervisor demo.

---

## 12. Suggested next steps

**Before any deployment**
1. Add authentication to `/api/admin/*` (API-key header dependency is enough for this scope).
2. Implement `RedisSessionStore` behind the existing `SessionStore` ABC and point slowapi at Redis —
   the dependency and container are already there.
3. Add a `.dockerignore` (`venv/`, `.git/`, `data/chroma_db/`, `__pycache__/`, `docs/resources/`).

**To unblock the plan**
4. Merge `salma` into `main` so the RAG improvements are the baseline.
5. Start Sprint 3: scaffold `frontend/` with Vite + React, RTL support for `ar`, and wire it to the
   existing endpoints (the response already carries `is_darija`, `is_urgent`, and `user_profile`
   flags the UI can render as badges).

**Quick wins**
6. Delete the unreachable block at [chain.py:455-461](backend/rag/chain.py#L455-L461) and the dead `MAX_MESSAGE_LENGTH` /
   `REDIS_URL` config (or wire them up).
7. Write a root `README.md` with setup, ingestion (`python -m backend.rag.embeddings`), run, and test
   commands — currently that knowledge exists only in docstrings.
8. Reconcile the model name across `docs/evaluation_llm.md`, `plan/sprint2/task3.md`, and `demo_cli.py`,
   and re-run the quality evaluation against the model actually configured.
9. Expand the Arabic knowledge base toward parity with French.
10. `git rm "'"`.
