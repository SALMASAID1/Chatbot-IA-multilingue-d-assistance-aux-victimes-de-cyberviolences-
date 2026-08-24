# EMC Helpline — Frontend

React interface for the multilingual cyberviolence-support assistant of
**CMRPI — Espace Maroc Cyberconfiance (EMC)**.

Supports **French**, **Modern Standard Arabic** and **Moroccan Darija** (Arabic
script and Arabizi), with full RTL layout.

---

## Requirements

| | |
|---|---|
| Node.js | **≥ 20.19** (`.nvmrc` pins 22 — the repo's `/usr/bin/node` 18 is EOL and will not run Vite 7) |
| npm | ≥ 10 |
| Backend | The FastAPI app in [`../backend`](../backend), reachable on `http://127.0.0.1:8000` |

```bash
nvm use            # reads .nvmrc
```

## Install

```bash
cd frontend
npm install
cp .env.example .env.local     # optional; defaults work with the Vite proxy
```

## Develop

```bash
# Terminal 1 — backend
cd .. && venv/bin/python -m uvicorn backend.main:app --reload --port 8000

# Terminal 2 — frontend
cd frontend && npm run dev     # http://localhost:5173
```

`VITE_API_BASE_URL` is empty by default, so the app calls same-origin `/api/…`
and Vite forwards it to `VITE_DEV_API_PROXY` (default `http://127.0.0.1:8000`).
No CORS configuration is needed for local development.

## Verify

```bash
npm run lint          # ESLint (flat config, jsx-a11y, React Compiler rules)
npm run typecheck     # tsc --noEmit, strict
npm test              # Vitest + Testing Library + MSW (offline, deterministic)
npm run build         # production bundle into dist/
npm run test:e2e      # Playwright against the built app, API mocked
npm run format        # Prettier
```

### Contract test against a running backend

Skipped by default. It never calls `POST /api/chat`, so it spends no Gemini quota:

```bash
EMC_LIVE_API=1 EMC_API_URL=http://127.0.0.1:8000 \
  npx vitest run src/lib/api/live-contract.test.ts
```

### Playwright browsers

The suite runs on the **system Google Chrome** (`channel: 'chrome'`), so no
browser download is required. If Chrome is unavailable:

```bash
npx playwright install chromium
# then drop `channel: 'chrome'` from playwright.config.ts
```

## Environment variables

Only `VITE_*` variables reach the browser bundle — **never put a secret in one**.

| Variable | Default | Purpose |
|---|---|---|
| `VITE_API_BASE_URL` | *(empty)* | Backend origin. Empty ⇒ same-origin `/api/…`. |
| `VITE_DEV_API_PROXY` | `http://127.0.0.1:8000` | Where `npm run dev` forwards `/api`. |
| `VITE_API_TIMEOUT_MS` | `45000` | Chat request timeout (RAG + Gemini can be slow). |

## Images

The welcome visual is produced by [`../scripts/fetch_google_images.py`](../scripts/fetch_google_images.py),
which searches through a structured API (SerpAPI, or Google CSE as an adapter),
downloads locally, strips EXIF, converts to WebP and records provenance.

```bash
cd ..
venv/bin/pip install -r scripts/requirements-images.txt

export SERPAPI_KEY=your_key                    # or GOOGLE_CSE_API_KEY + GOOGLE_CSE_CX
venv/bin/python scripts/fetch_google_images.py --dry-run
venv/bin/python scripts/fetch_google_images.py --count 2
venv/bin/python -m pytest scripts/tests -q     # offline tests for the script
```

Fetched assets land in `public/images/` as `review_required` in
[`assets-manifest.json`](public/images/assets-manifest.json). **The application
may only use assets a human has flipped to `approved`** — appearing in an image
search is not a licence. Credits are regenerated into
[`ATTRIBUTIONS.md`](public/images/ATTRIBUTIONS.md).

> No search API key is configured in this repository, so **no image has been
> downloaded**. `WelcomeIllustration.tsx` renders a built-in, dependency-free
> inline SVG instead.

## Docker

```bash
# Build and run just the frontend (nginx on :8080 inside the container)
docker build -t emc-helpline-frontend ./frontend
docker run --rm -p 5173:8080 -e API_UPSTREAM=http://host.docker.internal:8000 emc-helpline-frontend

# Or the whole stack from the repository root
docker compose up --build        # frontend :5173 · api :8000 · redis :6379
```

The image is multi-stage (`node:22-alpine` → `nginx:1.27-alpine`), runs as the
unprivileged `nginx` user, serves an SPA fallback, proxies `/api/` to
`$API_UPSTREAM`, and sets CSP, `X-Frame-Options: DENY`, `nosniff` and
`Referrer-Policy: no-referrer`. No secret is baked into the image.

---

## Architecture

```
src/
├─ app/          AppShell, providers, query client
├─ components/   Header, Dialog, SafeMarkdown, ServiceStatus, ErrorBoundary…
├─ features/
│  ├─ chat/      useChatController, timeline, composer, welcome
│  ├─ emergency/ verified contacts + the urgent-answer panel
│  ├─ feedback/  POST /api/chat/feedback
│  └─ help/      help & resources dialog
├─ i18n/         fr · ar · ary locales, direction handling
├─ lib/
│  ├─ api/       typed client, Zod schemas, error taxonomy, query hooks
│  └─ security/  URL allow-list, Markdown sanitization, session storage
├─ styles/       design tokens (Tailwind v4 `@theme`)
└─ types/        contract types mirroring backend/api/models/schemas.py
```

### Decisions worth knowing

- **No router.** The product is one conversation surface; help and confirmations
  are dialogs. A router would add a dependency without improving the experience.
- **No admin UI.** `GET/DELETE /api/admin/sessions` are unauthenticated on the
  backend, so the client offers no way to reach them, and a test asserts that.
- **The backend owns urgency.** There is no frontend keyword classifier;
  `is_urgent` from the API is the only trigger for the emergency panel.
- **Language ≠ answer language.** The interface language is a display choice.
  Message language is auto-detected server-side, so no `langue` override is sent
  and the interface never flips itself mid-conversation.
- **Sensitive data is not persisted.** Only the session id lives in
  `sessionStorage`; message contents are never written to storage and never
  logged in production. An ESLint rule blocks `localStorage`.
- **Markdown is sanitized, never `dangerouslySetInnerHTML`** (also ESLint-blocked).
  Only `http`, `https`, `mailto` and `tel` URLs are allowed to render as links.
- **Naive UTC timestamps.** The backend's `datetime.utcnow()` serialises without
  a timezone; `parseBackendDate` appends `Z` so times are not shifted.
