import json
import os
import sys
import time
from collections import defaultdict
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")

import httpx
from openai import AsyncOpenAI
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

BASE_DIR = Path(__file__).resolve().parent
APP_START_TIME = int(time.time())

from config import (
    CONCERNS,
    EXTRAS,
    ISSUES,
    RELATIONSHIPS,
    TONES,
    VIBES,
    YEARS_OPTIONS,
)
from models import CommentRequest
from prompts import build_system_prompt, build_user_prompt
from loguru import logger
from utils import clean_comment, get_count, increment_count

logger.remove()
logger.add(sys.stderr, level="INFO")

APPRISE_URL = os.environ.get("APPRISE_URL")
if APPRISE_URL:
    import apprise

    _notifier = apprise.Apprise()
    _notifier.add(APPRISE_URL)

    def _apprise_sink(message):
        record = message.record
        _notifier.notify(
            title=f"stopfowler {record['level'].name}",
            body=str(record["message"]),
        )

    logger.add(_apprise_sink, level="ERROR")

MODEL = os.environ.get("LLM_MODEL", "google/gemini-2.5-flash")

_client = None


def get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.environ["OPENROUTER_API_KEY"],
        )
    return _client


TURNSTILE_SITE_KEY = os.environ.get("TURNSTILE_SITE_KEY", "")
TURNSTILE_SECRET_KEY = os.environ.get("TURNSTILE_SECRET_KEY", "")
RATE_LIMIT_MAX = int(os.environ.get("RATE_LIMIT_MAX", "10"))
RATE_LIMIT_WINDOW = int(os.environ.get("RATE_LIMIT_WINDOW", "3600"))

_rate_limit_hits: dict[str, list[float]] = defaultdict(list)


def _get_client_ip(request: Request) -> str:
    return request.headers.get("cf-connecting-ip") or request.client.host


def _is_rate_limited(ip: str) -> bool:
    now = time.monotonic()
    hits = _rate_limit_hits[ip]
    _rate_limit_hits[ip] = [t for t in hits if now - t < RATE_LIMIT_WINDOW]
    if len(_rate_limit_hits[ip]) >= RATE_LIMIT_MAX:
        return True
    _rate_limit_hits[ip].append(now)
    return False


async def _verify_turnstile(token: str, ip: str) -> bool:
    if not TURNSTILE_SECRET_KEY:
        return True
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://challenges.cloudflare.com/turnstile/v0/siteverify",
            data={"secret": TURNSTILE_SECRET_KEY, "response": token, "remoteip": ip},
        )
    return resp.json().get("success", False)


app = FastAPI()
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}


@app.get("/whats-going-on", response_class=HTMLResponse)
async def whats_going_on(request: Request):
    return templates.TemplateResponse(
        request,
        "whats-going-on.html",
        {
            "issues": ISSUES,
            "comment_count": get_count(),
            "cache_bust": APP_START_TIME,
        },
    )


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "concerns": CONCERNS,
            "vibes": VIBES,
            "extras": EXTRAS,
            "relationships": RELATIONSHIPS,
            "years_options": YEARS_OPTIONS,
            "tones": TONES,
            "issues": ISSUES,
            "comment_count": get_count(),
            "turnstile_site_key": TURNSTILE_SITE_KEY,
            "cache_bust": APP_START_TIME,
        },
    )


@app.post("/generate")
async def generate(request: Request):
    ip = _get_client_ip(request)

    if _is_rate_limited(ip):
        logger.warning("rate limited ip={}", ip)
        return JSONResponse(
            {"error": "Too many requests. Please try again later."}, status_code=429
        )

    form = await request.form()

    turnstile_token = str(form.get("cf-turnstile-response", ""))
    if TURNSTILE_SECRET_KEY and not await _verify_turnstile(turnstile_token, ip):
        logger.warning("turnstile failed ip={}", ip)
        return JSONResponse(
            {"error": "Bot check failed. Please refresh and try again."},
            status_code=403,
        )

    form_data = {
        "name": str(form.get("name", "")),
        "address": str(form.get("address", "")),
        "concerns": [str(v) for k, v in form.multi_items() if k == "concerns"],
        "vibe": str(form.get("vibe", "concerned")),
        "tone": str(form.get("tone", "conversational")),
        "relationship": str(form.get("relationship", "")),
        "years": str(form.get("years", "")),
        "extras": [str(v) for k, v in form.multi_items() if k == "extras"],
        "custom_note": str(form.get("custom_note", "")),
    }
    req = CommentRequest(**form_data)

    system_prompt = build_system_prompt(
        tone=req.tone_instruction, vibe=req.vibe_instruction
    )
    user_prompt = build_user_prompt(
        name=req.name,
        relationship=req.relationship_label,
        years_desc=req.years_description,
        address=req.address,
        concern_text=req.concern_text,
        extras_text=req.extras_text,
        custom_note=req.custom_note,
    )

    async def stream_comment():
        full_text = ""
        t_start = time.monotonic()
        t_first_token = None
        token_count = 0
        try:
            stream = await get_client().chat.completions.create(
                model=MODEL,
                max_tokens=2048,
                stream=True,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
            async for chunk in stream:
                delta = chunk.choices[0].delta if chunk.choices else None
                if delta and delta.content:
                    full_text += delta.content
                    token_count += 1
                    if t_first_token is None:
                        t_first_token = time.monotonic()
                        logger.info(
                            "TIMING first token: {:.1f}s", t_first_token - t_start
                        )
                    yield f"data: {json.dumps({'text': delta.content})}\n\n"

            t_done = time.monotonic()
            logger.info(
                "TIMING total={:.1f}s first_token={:.1f}s streaming={:.1f}s tokens={} model={}",
                t_done - t_start,
                (t_first_token or t_done) - t_start,
                t_done - (t_first_token or t_done),
                token_count,
                MODEL,
            )

            if not full_text:
                yield f"data: {json.dumps({'error': 'No response generated. Please try again.'})}\n\n"
                return

            if "===COMMENT_SPLIT===" in full_text:
                parts = full_text.split("===COMMENT_SPLIT===", 1)
                comment_annexation = clean_comment(parts[0])
                comment_housing = clean_comment(parts[1])
            else:
                comment_annexation = clean_comment(full_text)
                comment_housing = ""

            count = increment_count()
            logger.info("comments #{} generated", count)
            yield f"data: {json.dumps({'done': True, 'count': count, 'annexation': comment_annexation, 'housing': comment_housing})}\n\n"

        except Exception:
            logger.exception("Unexpected error during generation")
            yield f"data: {json.dumps({'error': 'Something went wrong. Please try again.'})}\n\n"

    return StreamingResponse(stream_comment(), media_type="text/event-stream")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5111)
