# InstaVidGen

A studio for Instagram quote content. It renders **Reels (MP4)** and **Posts (PNG)** from a curated
background library. An AI pipeline (LangChain + LangGraph on Groq) writes the quotes, captions and hashtags.

- **Backend:** FastAPI, Pydantic v2, LangChain (`langchain-groq`), LangGraph, Pillow, ffmpeg (bundled via `imageio-ffmpeg`), managed with **uv**
- **Frontend:** Next.js 16 (App Router, TypeScript), Tailwind CSS v4, shadcn/ui

## Quick start

Requirements: [uv](https://docs.astral.sh/uv/), Node.js 20+, and a [Groq API key](https://console.groq.com/keys) for the AI features.

```bash
# 1. Backend  →  http://localhost:8002  (API docs at /docs)
cd backend
cp .env.example .env        # then set GROQ_API_KEY
uv sync
uv run fastapi dev --port 8002

# 2. Frontend  →  http://localhost:3000   (in a second terminal)
cd frontend
npm install
npm run dev
```

The frontend proxies `/api/*` and `/media/*` to the backend (see `frontend/next.config.ts`). The
browser only talks to one origin. If the backend is somewhere else, set `BACKEND_URL` before running `npm run dev`.

Without a key you can still write quotes by hand and render. You can also paste a personal key in
the app's **Settings**. It is stored in the browser and sent as the `X-Groq-Api-Key` header.

## Features

- **AI quotes:** pick a theme and an optional voice (Seneca, Nietzsche, Rumi…). The LangGraph
  workflow drafts candidates, then cleans and de-duplicates them against your recent quotes. If it
  has too few, it loops back for more.
- **Captions & hashtags:** generated per quote and saved alongside every render.
- **Live preview:** server-rendered and debounced, so what you see is exactly what gets exported.
- **Design controls:** five formats at Instagram's native resolutions (1080×1350, 1080×1920,
  1080×1080, 1920×1080, 1440×1080), 24 font styles, text position, size (auto-shrinks to fit),
  background dim, and attribution.
- **Reels:** H.264 / yuv420p MP4 with fade-in/out. Plays in every browser and uploads to
  Instagram as-is.
- **Batch render:** up to 20 reels or posts in the background, each with a fresh AI quote and caption
  and a different background. Progress shows live.
- **Library:** browse, play, download, copy captions and delete everything you've rendered.

## Project structure

```
backend/
├── app/
│   ├── main.py                 # FastAPI app factory: CORS, error handling, static media
│   ├── core/                   # settings (pydantic-settings), catalog, domain errors
│   ├── schemas/                # Pydantic request/response models (camelCase on the wire)
│   ├── api/
│   │   ├── deps.py             # dependency injection (services, per-request Groq key)
│   │   └── routes/             # system · ai · render · media · batches
│   └── services/
│       ├── ai/                 # ChatGroq factory, prompts, LangGraph workflow, facade
│       ├── media/              # assets, Pillow composer, ffmpeg encoder, library, renderer
│       ├── batch.py            # background batch jobs with pollable progress
│       └── container.py        # wires services together
├── assets/                     # backgrounds/ and fonts/ (OFL licensed)
├── storage/                    # generated videos, posts, thumbnails (git-ignored)
├── tests/                      # pytest: API, rendering, LangGraph workflow (fake LLM)
└── pyproject.toml · uv.lock

frontend/src/
├── app/                        # layout (fonts, providers) and page
├── components/
│   ├── studio/                 # header, quote/design/background panels, preview, dialogs
│   ├── library/                # library grid, media thumbnails, viewer
│   └── ui/                     # shadcn/ui components
├── hooks/                      # local storage, debounce, clipboard, AI settings
└── lib/                        # typed API client, types, formatting helpers
```

## API

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/api/health` | Liveness |
| GET | `/api/config` | Themes, voices, formats, fonts, backgrounds, models, stats |
| GET | `/api/backgrounds/{id}/thumbnail` | Cached JPEG thumbnail |
| POST | `/api/ai/quote` | Generate a quote (LangGraph workflow) |
| POST | `/api/ai/caption` | Generate a caption + hashtags |
| POST | `/api/render/preview` | Preview as a JPEG data URI |
| POST | `/api/render/post` | Render a PNG post |
| POST | `/api/render/video` | Render an MP4 reel |
| GET / DELETE | `/api/media` · `/api/media/{kind}/{filename}` | List / delete renders |
| POST / GET | `/api/batches` · `/api/batches/{id}` | Start / poll a batch job |

## Configuration (`backend/.env`)

| Variable | Default | |
| --- | --- | --- |
| `GROQ_API_KEY` | — | Required for AI features (or set per user in the UI) |
| `GROQ_MODEL` | `openai/gpt-oss-120b` | Any Groq chat model that supports tool calling |
| `CORS_ORIGINS` | `["http://localhost:3000","http://127.0.0.1:3000"]` | Only needed for direct browser→API calls |

A `.env` at the project root is also read (`backend/.env` wins).

## Development

```bash
cd backend && uv run pytest && uv run ruff check app tests   # tests + lint
cd frontend && npm run typecheck && npm run lint && npm run format
```
