# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository layout

Monorepo with two independent apps:

- `frontend/` — Vue 3 + Vite + TypeScript SPA (Pinia, Vue Router, Tailwind, Three.js, GSAP, ECharts/ApexCharts, CodeMirror). Deployed to GitHub Pages under base path `/MyPortfolio/`.
- `backend/` — FastAPI (Python) single-file app (`backend/main.py`) with SQLAlchemy + PostgreSQL, JWT auth + refresh tokens, slowapi rate limiting, BeautifulSoup GitHub scraper, and AI integration (Anthropic Claude + Google Gemini). Deployed on Render.
- Root `package.json` exists but the real frontend `package.json` is inside `frontend/`.

The two apps are connected only via HTTP. In dev, Vite proxies `/api` → `http://127.0.0.1:8000` (`frontend/vite.config.ts`). In prod, `frontend/src/api.ts` points axios at the hardcoded Render URL `https://portfolio-api-a21d.onrender.com`.

## Common commands

Frontend (run from `frontend/`):

```bash
npm install
npm run dev          # vite dev server, http://localhost:5173
npm run build        # parallel: type-check + vite build, then copies dist/index.html → dist/404.html (SPA-only fallback, NO prerender)
npm run build:ssg    # vite build + node scripts/prerender.mjs + copy 404.html — USE THIS FOR DEPLOY (real prerendered HTML for SEO)
npm run build-only   # vite build only (skips type-check)
npm run type-check   # vue-tsc --build
npm run lint         # eslint . --fix --cache
npm run format       # prettier --write src/
npm run test:unit    # vitest (jsdom). Single test: npx vitest run path/to/file.spec.ts -t "test name"
npm run preview      # preview built dist
```

Node version is pinned in `frontend/package.json` engines: `^20.19.0 || >=22.12.0`.

Backend (run from `backend/`, with venv active):

```bash
python -m venv venv
venv\Scripts\activate          # Windows (this repo's primary env)
# source venv/bin/activate     # macOS/Linux
pip install -r requirements.txt
uvicorn main:app --reload      # http://localhost:8000
```

A `.env` is required. Required vars: `SECRET_KEY`, `DATABASE_URL`, `ADMIN_USER`, `ADMIN_PASSWORD`. **`SECRET_KEY` and `DATABASE_URL` have NO fallback** — `main.py` raises `RuntimeError` at import time if either is missing/empty. Don't reintroduce fallbacks.

There is no backend test suite or linter configured.

## Architecture notes

### Backend (`backend/main.py`)

Everything lives in this one file: env loading, SQLAlchemy engine/`SessionLocal`/`Base`, ORM models, Pydantic schemas, JWT helpers, slowapi limiter, CORS, security-headers + traffic-log middleware, route handlers, and the GitHub scraper. Follow the existing section-comment structure (`# 0. 環境變數`, `# 1. 資料庫連線`, `# 2. 資料庫模型`, …) when adding features.

CMS resources are Projects, Blog Posts, and Lab code snippets (HTML/CSS/JS playgrounds, accessed by random `slug`).

**Auth model (important — non-trivial):**
- `oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/login")` + `get_current_admin` dependency. EVERY write route (POST/PUT/DELETE on projects/posts/snippets/upload) MUST take `current_admin: AdminModel = Depends(get_current_admin)`. GETs are public but filter `is_published == True`.
- Two-token JWT flow: short-lived **access token** (15 min, HS256, signed with `SECRET_KEY`) + opaque **refresh token** (7 days, `secrets.token_urlsafe(32)`, sha256-hashed in `refresh_tokens` table). `/api/login` returns both. `/api/refresh` rotates the refresh token (deletes old row, issues new). `/api/logout` deletes the refresh row. Don't let access tokens live longer or skip rotation.
- IP-based login lockout: 3 failures in 3 minutes from same IP → 429. IPs come from `get_client_ip(request)` which reads `X-Forwarded-For` (Render is behind a proxy — `request.client.host` alone is wrong).
- Rate limits via `slowapi` decorators on `/api/login`, `/api/upload`, `/api/github_contributions`, `/api/system_status`. Limiter key function wraps `get_client_ip`.
- **CORS `allow_methods` is an explicit whitelist**, NOT `["*"]`. When adding a new HTTP method (e.g., a `PATCH` route), you MUST add the method to the `allow_methods` list in `CORSMiddleware` config or the browser preflight will fail. Current list: `["GET","POST","PUT","PATCH","DELETE","OPTIONS"]`.

**Uploads:** `/api/upload` whitelists extensions/MIME (jpg/jpeg/png/gif/webp), enforces 5 MB chunked, deletes partial files on overflow. Public reads go through a custom `/static/uploads/{filename}` handler with regex validation, NOT the `StaticFiles` mount. Don't bypass either.

**`api_logs` table:** the `log_api_requests` middleware writes one row per `/api/*` request. A 0.1%-probability cleanup deletes rows older than 30 days — don't remove this or the table will grow unbounded.

**Schema migrations:** `Base.metadata.create_all` only CREATES new tables, never ALTERs. If you add a column to an existing model (e.g., `ProjectModel.is_published` was added this way), you MUST run manual SQL on the deployed Postgres (`ALTER TABLE ... ADD COLUMN ...`).

**AI integration (`/api/ai/*`):**
- `/api/ai/assist` — admin-only writing helper, calls **Claude Haiku 4.5** via `anthropic` SDK. 4 actions: `polish` / `translate_en` / `summarize` / `title_suggestions`. Rate-limited 20/min.
- `/api/ai/chat` — public visitor chatbot, calls **Gemini 2.5 Flash** via `google-genai` SDK. Stuffs published projects + 20 latest posts (truncated) into the system prompt as context. Rate-limited 10/min, max 20 messages per request, 8000 chars total.
- Both SDK imports are **lazy** (inside the handler, wrapped in try/except ImportError → 503). The app boots even without the SDKs installed. Don't move them to top-level.
- Both endpoints check their API key (`ANTHROPIC_API_KEY` / `GEMINI_API_KEY`) and return 503 if missing — keys are optional, the rest of the app works without them.

### Frontend (`frontend/src`)

- `api.ts` — single shared axios instance. Always import this (`import api from '@/api'`) rather than calling axios directly. It carries the auth interceptors:
  - Request interceptor attaches `Authorization: Bearer <localStorage.admin_token>`.
  - Response interceptor implements **single-flight refresh-on-401**: on 401, calls `/api/refresh` exactly once (shared `refreshPromise` for concurrent failures), updates BOTH `admin_token` and `admin_refresh_token` in localStorage (refresh tokens rotate), retries the original request. On refresh failure, clears storage and redirects to `/login`. The internal refresh call uses **bare `axios`**, not `api`, to avoid recursive interceptors. Don't break this pattern.
- Token storage: `localStorage` keys `admin_token` (access) and `admin_refresh_token` (refresh). Survives tab close. Logout (`AdminView.vue`) calls `POST /api/logout` then clears both keys.
- Backend base URL comes from `import.meta.env.VITE_API_BASE_URL` (set in `frontend/.env.production`). Empty in dev so the Vite `/api` proxy in `vite.config.ts` takes over.
- `router/index.ts` — Vue Router; admin/dashboard routes guard against missing `admin_token`.
- Path alias `@` → `frontend/src`.

**Theming:** All visual styling MUST go through CSS variables defined in `src/assets/css/Theme.css` (`--bg-color`, `--card-bg`, `--text-color`, `--milk-tea`, `--milk-tea-dark`, `--gradient-text`, `--btn-bg`, `--btn-hover`, `--border-color`, …). The site has 3 modes — `:root` defaults, `body.theme-dark`, `body.theme-light` — and all 3 redefine the same variable names. Hardcoding hex colors in components breaks light-mode. When adding a new component, copy the variable names from an existing themed component (e.g., `ChatWidget.vue`).

**Image URL convention:** `cover_image` (and any backend-served file) is stored in DB as a **relative path** like `/static/uploads/xxx.jpg`. Components must prefix it with `import.meta.env.VITE_API_BASE_URL || ''` at render time. Don't store full URLs — that breaks across dev/prod environments. Existing helpers: `getImageUrl(path)` in `HomeView.vue` / `BlogView.vue`, `getCoverUrl(img)` in `PostDetailView.vue`. **Never put `import.meta.env` directly in a Vue template expression** — it triggers a parser error; compute it in `<script>` first.

**SSG / prerender:** Production deploys use `npm run build:ssg`, which runs Vite build then `frontend/scripts/prerender.mjs`. The script spins up a local `sirv` server on `dist/`, launches puppeteer, and navigates to each prerendered route (`/`, `/blog`, `/projects`, `/lab`, `/blog/:id` for every published post fetched from the production API). It captures the rendered HTML and writes it to `dist/<route>/index.html`, plus generates `dist/sitemap.xml`. API calls during prerender are intercepted and proxied to `https://portfolio-api-a21d.onrender.com` with CORS headers added. **Browser-only code (Three.js, GSAP, CodeMirror) does NOT need guarding** — puppeteer runs real Chrome, so `window`/`document` exist. Render free-tier cold starts can make the first prerender slow; timeouts are set to 60–120s.

**ChatWidget mounting:** `src/components/ChatWidget.vue` is mounted in `App.vue` and hidden on routes containing `/admin`, `/login`, or `/dashboard`. Chat history persists in `sessionStorage` (key `mike_chat_history_v1`), capped at 20 messages.

### Deployment specifics that affect code changes

- Vite `base: '/MyPortfolio/'` — any hardcoded asset paths must respect this base, or use Vite's URL handling. Don't change the base without updating GitHub Pages config.
- Both build scripts copy `dist/index.html` to `dist/404.html` so GitHub Pages serves the SPA on deep links. Don't remove that step.
- **Use `npm run build:ssg`, NOT `npm run build`, for production deploys** — only the `:ssg` variant prerenders pages for SEO. The plain `build` is kept as a fast fallback.
- `frontend/deploy.sh` is the GitHub Pages deploy script (must run from `frontend/`, in Git Bash on Windows). It re-inits a git repo inside `dist/` and force-pushes `master:gh-pages`. **If you re-run it without `rm -rf dist` first, the stale `dist/.git` may say "nothing to commit" and silently skip the push** — always wipe `dist/` before redeploying. Note: `deploy.sh` itself still calls `npm run build` (not `:ssg`), so the recommended sequence is `rm -rf dist && npm run build:ssg && sh deploy.sh` (deploy.sh's internal build is a no-op when dist is fresh — or you can edit deploy.sh to skip rebuild).
- Prod backend URL lives in `frontend/.env.production` as `VITE_API_BASE_URL`. If the Render URL changes, update it there (not in `api.ts`).
- GitHub Pages must be set to **Deploy from a branch → gh-pages → / (root)**. If the repo visibility flips (private → public), GitHub may reset Pages to GitHub Actions — re-set the source manually.
