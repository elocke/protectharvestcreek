"""Sanitization, comment cleaning, and counter helpers."""

import re
from pathlib import Path

_INJECTION_PATTERNS = re.compile(
    r"|".join(
        [
            r"ignore\s+(all\s+)?(previous|prior|above)\s+(instructions|prompts)",
            r"forget\s+(everything|all|your)\b",
            r"you\s+are\s+now\b",
            r"new\s+(instructions|role|persona)\b",
            r"disregard\s+(all|any|the|your)\b",
            r"override\s+(system|instructions|rules)\b",
            r"act\s+as\s+(if|a|an|though)\b",
            r"pretend\s+(you|to\s+be)\b",
            r"do\s+not\s+follow\b",
            r"stop\s+being\b",
            r"jailbreak",
            r"DAN\s+mode",
        ]
    ),
    re.IGNORECASE,
)


def sanitize_freetext(value: str, max_len: int) -> str:
    """Sanitize user freetext to prevent prompt injection."""
    text = value.strip()[:max_len]
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
    text = _INJECTION_PATTERNS.sub("", text)
    text = re.sub(
        r"(SYSTEM|ASSISTANT|USER|<\|im_start\||<\|im_end\||\[INST\]|\[/INST\])",
        "",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(r"</?[a-zA-Z][^>]*>", "", text)
    return text.strip()


def clean_comment(raw: str) -> str:
    """Strip preamble/postamble that LLMs sometimes add around the actual comment."""
    text = raw.strip()
    # Strip preamble
    text = re.sub(
        r"^(?:Here\'?s?|Sure|Certainly|Of course|I\'ve)[^\n]*\n+",
        "",
        text,
        flags=re.IGNORECASE,
    ).strip()

    # Find the signature line (last short line that looks like a name) and truncate after it.
    # A signature is typically 1-3 words with minimal punctuation (just periods allowed).
    lines = text.split("\n")
    last_sig = -1
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue
        words = stripped.split()
        # Name-like signature: 1-3 words, only periods allowed for abbreviations, no other punctuation
        if 1 <= len(words) <= 3 and not re.search(
            r"[!?;:,()\"'\[\]@#$%^&*\-+=]", stripped
        ):
            # Must not look like a sentence (no verbs, articles, or sentence starters)
            if not re.match(
                r"(?:I |We |The |This |That |It |My |Our |Please |Thank |And |But |Or |However|Because|Since)",
                stripped,
                re.IGNORECASE,
            ):
                last_sig = i

    if last_sig >= 0 and last_sig < len(lines) - 1:
        text = "\n".join(lines[: last_sig + 1]).strip()

    return text


# ---------------------------------------------------------------------------
# Comment counter (simple file-based)
# ---------------------------------------------------------------------------
COUNTER_FILE = Path(__file__).resolve().parent / "data" / "counter.txt"


def get_count() -> int:
    try:
        return int(COUNTER_FILE.read_text().strip())
    except (FileNotFoundError, ValueError):
        return 0


def increment_count() -> int:
    COUNTER_FILE.parent.mkdir(exist_ok=True)
    n = get_count() + 1
    COUNTER_FILE.write_text(str(n))
    return n
