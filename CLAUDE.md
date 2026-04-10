# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**protectharvestcreek** (formerly `stopfowler`) — self-hosted web app for Bozeman, MT neighbors to generate personalized public comments opposing the Fowler Avenue rezoning (higher-density apartments on a road extension with insufficient space) and the related Hanson Lane annexation. Click-to-vibe UX designed for non-technical users.

## Stack

- **Backend**: FastAPI + Python 3.12 (managed with `uv`)
- **Frontend**: Jinja2 templates + vanilla JS + Pico CSS v2 (CDN) — no build step
- **AI**: Claude Agent SDK with streaming
- **Database**: None — stateless, plus a simple file-based comment counter

## Commands

```bash
uv run python app.py                   # Dev server on :5111
ANTHROPIC_API_KEY=sk-... uv run python app.py  # With streaming SDK
uv add <package>                        # Add dependency
```

## Architecture

Modular Python backend with two routes:
- `GET /` — form page with 4-step click-to-vibe UX + single "Generate Both Comments" button
- `POST /generate` — generates BOTH comments in a single LLM call, returns SSE stream (`text/event-stream`)

### Two Issues (one LLM call)
The app generates comments for two separate city processes in a single API call using a `===COMMENT_SPLIT===` delimiter:
- **Hanson Lane Annexation** (App 25775) — R-B zoning, email to `comments@bozeman.net`
- **Fowler Housing Development** (Oak to Annie) — email to `agenda@bozeman.net`

Each has its own email target, subject line, and system prompt context in `config.py`'s `ISSUES` dict. The `done` SSE event includes both `annexation` and `housing` fields with the split/cleaned text.

### AI Backend
Uses Claude Agent SDK (`claude_agent_sdk.query()`) with streaming. Text appears word-by-word in the browser.

### SSE Protocol
The `/generate` endpoint returns `text/event-stream` with JSON payloads:
- `{"text": "chunk"}` — incremental text (SDK) or full text (CLI fallback)
- `{"done": true, "count": N}` — generation complete, includes updated counter
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
`docs/*.md` files loaded at startup into `REFERENCE_DOCS` string. Add/edit docs and restart to update.

### Comment Counter
Simple file-based counter at `data/counter.txt`. Incremented on each successful generation. Displayed in hero banner.

## Key Files

- `app.py` — FastAPI routes and SSE streaming
- `config.py` — allowlists (CONCERNS, VIBES, EXTRAS, etc.) and ISSUES dict
- `prompts.py` — system/user prompt construction, reference doc loading
- `utils.py` — input sanitization, comment cleaning, file-based counter
- `templates/index.html` — Jinja2 template (HTML structure only)
- `static/css/style.css` — all CSS
- `static/js/app.js` — streaming JS, calendar export, result rendering
- `docs/` — reference documents for AI prompt context
- `data/counter.txt` — comment counter (auto-created)

## Email Flow

1. User clicks "Copy to Clipboard"
2. User clicks "Open Email App" (mailto link pre-addressed to agenda@bozeman.net)
3. User pastes and sends from their own email client
