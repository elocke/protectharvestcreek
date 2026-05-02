# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**protectharvestcreek** (formerly `stopfowler`) — self-hosted web app for Bozeman, MT neighbors to generate personalized public comments opposing the Fowler Avenue rezoning (higher-density apartments on a road extension with insufficient space) and the related Hanson Lane annexation. Click-to-vibe UX designed for non-technical users.

## Stack

- **Backend**: FastAPI + Python 3.12 (managed with `uv`)
- **Frontend**: Jinja2 templates + vanilla JS + Pico CSS v2 (CDN) — no build step
- **AI**: OpenAI async SDK (`AsyncOpenAI`) pointed at OpenRouter's OpenAI-compatible endpoint. Streaming chat.completions. Model selected via `LLM_MODEL` env var. Production target: `anthropic/claude-sonnet-4.6`. Code default fallback: same.
- **Database**: None — stateless, plus a simple file-based comment counter

## Commands

```bash
OPENROUTER_API_KEY=sk-or-... uv run python app.py   # Dev server on :5111
uv add <package>                                    # Add dependency
```

## Env Vars

- `OPENROUTER_API_KEY` — required for `/generate` (the LLM call). Server still starts without it; the call fails at request time.
- `LLM_MODEL` — OpenRouter model slug. Defaults to `anthropic/claude-sonnet-4.6`. Override to use Haiku, Gemini, etc.
- `TURNSTILE_SITE_KEY` / `TURNSTILE_SECRET_KEY` — optional Cloudflare Turnstile bot check. If `TURNSTILE_SECRET_KEY` is unset, verification is skipped.
- `RATE_LIMIT_MAX` (default 10) / `RATE_LIMIT_WINDOW` (default 3600s) — per-IP rate limit on `/generate`.
- `APPRISE_URL` — optional Apprise notification target for ERROR-level logs.

## Architecture

Modular Python backend with two routes:
- `GET /` — form page with 4-step click-to-vibe UX + single "Generate Both Comments" button
- `POST /generate` — generates BOTH comments in a single LLM call, returns SSE stream (`text/event-stream`)

### Two Issues (one LLM call)
The app generates comments for two separate city processes in a single API call using a `===COMMENT_SPLIT===` delimiter:
- **Hanson Lane Annexation** (App 25775) — R-B zoning, email to `comments@bozeman.net`
- **Fowler Housing Development** (Oak to Annie) — email to `comments@bozeman.net`

Each has its own email target, subject line, and system prompt context in `config.py`'s `ISSUES` dict. The `done` SSE event includes both `annexation` and `housing` fields with the split/cleaned text.

### AI Backend
Uses `AsyncOpenAI` (`openai` package) pointing at `https://openrouter.ai/api/v1`. The streaming `chat.completions.create` call sends `system_prompt` + `user_prompt`, with `temperature=0.9`, `top_p=0.95`, `frequency_penalty=0.3`, `presence_penalty=0.3` (sampling tuned to reduce templatey AI output — Bozeman commissioners flagged AI-style writing as biasing the prior round of comments). Text appears word-by-word in the browser via SSE deltas.

### SSE Protocol
The `/generate` endpoint returns `text/event-stream` with JSON payloads:
- `{"text": "chunk"}` — incremental text from the streaming LLM call
- `{"done": true, "count": N, "annexation": "...", "housing": "..."}` — generation complete, both split comments included
- `{"error": "message"}` — error occurred

Frontend JS reads the stream with `fetch()` + `ReadableStream` and progressively updates the DOM.

### Prompt Injection Protection
User input never controls prompt instructions. All choices are checkbox/radio mapped to server-side allowlists:
- `CONCERNS` — `(chip_label, prompt_description)` tuples
- `VIBES` — `(emoji, chip_label, prompt_instruction)` tuples
- `EXTRAS` — `(chip_label, prompt_instruction)` tuples
- `RELATIONSHIPS` — `(emoji, chip_label)` tuples
- `YEARS_OPTIONS` — `(chip_label, prompt_phrase)` tuples
- `TONES` — `(chip_label, prompt_instruction)` tuples

Only name, address, and custom_note are freetext — all truncated and slotted into data fields.

### Reference Documents
`docs/*.md` files loaded at startup into `REFERENCE_DOCS` string and injected into the system prompt. Glob is non-recursive, so `docs/export/` (citizen PII, gitignored) and `docs/superpowers/` (planning notes) are not loaded. Add/edit docs and restart to update.

### Live Deadline
`config.py:DEADLINE` is the single source of truth for the active public-comment deadline (date, display string, ICS values, meeting body). `app.py` passes it into both `TemplateResponse` contexts; templates render `{{ deadline.* }}`; `static/js/app.v2.js` reads ICS values from server-rendered `<meta name="deadline-*">` tags. Pivoting to a new deadline = edit `DEADLINE` only.

### Anti-AI-Tells in Prompt
`prompts.py:build_system_prompt` includes an explicit AVOID AI WRITING TELLS section: banned vocabulary, banned structural patterns, em-dash limits, sentence-rhythm guidance, and a directive to draw on `docs/talking_points_may_2026.md` arguments without copying verbatim. This is the primary lever for reducing AI-style output on top of the sampling parameters.

### Comment Counter
Simple file-based counter at `data/counter.txt`. Incremented on each successful generation. Displayed in hero banner.

## Key Files

- `app.py` — FastAPI routes and SSE streaming
- `config.py` — allowlists (CONCERNS, VIBES, EXTRAS, etc.), ISSUES dict, `DEADLINE` constant
- `prompts.py` — system/user prompt construction, reference doc loading, AVOID AI WRITING TELLS section
- `utils.py` — input sanitization, comment cleaning, file-based counter
- `templates/index.html` / `templates/whats-going-on.html` — Jinja2 templates; deadline meta tags read by JS
- `static/css/style.css` — all CSS
- `static/js/app.v2.js` — streaming JS, calendar export, result rendering
- `docs/*.md` — reference documents auto-loaded into prompt context
- `data/counter.txt` — comment counter (auto-created)

## Email Flow

1. User clicks "Copy to Clipboard"
2. User clicks "Open Email App" (mailto link pre-addressed to comments@bozeman.net)
3. User pastes and sends from their own email client
