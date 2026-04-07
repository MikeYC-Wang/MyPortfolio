# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository layout

Monorepo with two independent apps:

- `frontend/` — Vue 3 + Vite + TypeScript SPA (Pinia, Vue Router, Tailwind, Three.js, GSAP, ECharts/ApexCharts, CodeMirror). Deployed to GitHub Pages under base path `/MyPortfolio/`.
- `backend/` — FastAPI (Python) single-file app (`backend/main.py`, ~565 lines) with SQLAlchemy + PostgreSQL, JWT auth (python-jose + passlib/bcrypt), and a BeautifulSoup GitHub-contributions scraper. Deployed on Render.
- Root `package.json` exists but the real frontend `package.json` is inside `frontend/`.

The two apps are connected only via HTTP. In dev, Vite proxies `/api` → `http://127.0.0.1:8000` (`frontend/vite.config.ts`). In prod, `frontend/src/api.ts` points axios at the hardcoded Render URL `https://portfolio-api-a21d.onrender.com`.

## Common commands

Frontend (run from `frontend/`):

```bash
npm install
npm run dev          # vite dev server, http://localhost:5173
npm run build        # parallel: type-check + vite build, then copies dist/index.html → dist/404.html (GitHub Pages SPA fallback)
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

A `.env` is required (see README). Key vars used in `main.py`: `SECRET_KEY`, `DATABASE_URL` (PostgreSQL). Defaults in code are placeholders — real secrets must come from `.env`.

There is no backend test suite or linter configured.

## Architecture notes

### Backend (`backend/main.py`)

Everything lives in this one file: env loading, SQLAlchemy engine/`SessionLocal`/`Base`, ORM models (`ProjectModel`, `PostModel`, `CodeSnippetModel`, `SkillModel`, …), Pydantic schemas, JWT helpers (`OAuth2PasswordBearer` at `tokenUrl="api/login"`), CORS middleware, route handlers, and the GitHub scraper. When adding features, follow the existing section-comment structure (`# 0. 環境變數`, `# 1. 資料庫連線`, `# 2. 資料庫模型`, …) rather than introducing new modules unless the file grows significantly.

CMS resources are Projects, Blog Posts, and Lab code snippets (HTML/CSS/JS playgrounds, accessed by random `slug`). Auth-protected admin routes use the `oauth2_scheme` dependency. There is also middleware-based traffic monitoring and login IP lockout (anti brute-force) — preserve these when refactoring auth.

`backend/static/` is served via `StaticFiles` for uploaded images.

### Frontend (`frontend/src`)

- `api.ts` — single shared axios instance. Always import this rather than calling axios directly, so the dev proxy + prod baseURL switch keeps working.
- `router/index.ts` — Vue Router; views in `src/views/` map to top-level routes (`HomeView`, `BlogView`, `PostDetailView`, `ProjectView`, `LabView`, `LabEditorView`, `LoginView`, `AdminView`, `DashboardView`, `NotFoundView`). Admin/Dashboard routes are auth-gated.
- `stores/` — Pinia stores.
- `composables/` — reusable Vue composition functions (Three.js scene setup, GSAP animations, terminal effect, etc. live here or in `components/`).
- Path alias `@` → `frontend/src` (configured in `vite.config.ts` and `tsconfig`).

### Deployment specifics that affect code changes

- Vite `base: '/MyPortfolio/'` — any hardcoded asset paths must respect this base, or use Vite's URL handling. Don't change the base without updating GitHub Pages config.
- The build script copies `dist/index.html` to `dist/404.html` so GitHub Pages serves the SPA on deep links. Don't remove that step.
- `frontend/deploy.sh` is the GitHub Pages deploy script.
- Prod backend URL is hardcoded in `src/api.ts`; if the Render URL changes, update it there.
