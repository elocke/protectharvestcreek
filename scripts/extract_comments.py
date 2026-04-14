"""Extract submitter info and comment bodies from exported public-comment PDFs.

Usage:
    uv run --with "" python scripts/extract_comments.py

Reads /tmp/pdfext/{folder}__{basename}.txt (already produced by pdftotext -layout)
and emits docs/export/extracted.json with one record per comment.
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path

TXT_DIR = Path("/tmp/pdfext")
HTML_DIR = Path("/tmp/pdfhtml")
OUT_PATH = Path("/home/elocke/dev/stopfowler/docs/export/extracted.json")

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
MAILTO_LINK_RE = re.compile(
    r'<a href="mailto:([^"?]+)[^"]*">([^<]+)</a>', re.IGNORECASE
)
HEADER_RE = re.compile(r"^(From|To|Cc|Subject|Date|Attachments):\s*(.*)$", re.MULTILINE)

CITY_DOMAINS = {"bozeman.net", "bozemanmt.gov"}
ADVOCACY_DOMAINS = {"harvestcreekmt.org", "harvestcreek.org"}
EXCLUDE_EMAILS = {
    "comments@bozeman.net",
    "contact@harvestcreekmt.org",
    "contact@harvestcreek.org",
    "agenda@bozeman.net",
    "mailer@payhoa.com",
}


@dataclass
class Comment:
    folder: str  # "hanson" or "fowler"
    file: str  # original PDF basename
    from_header: str = ""
    from_email: str = ""  # best-guess sender email
    submitter_name: str = ""  # from filename / From header
    to_header: str = ""
    cc_header: str = ""
    subject: str = ""
    date: str = ""
    body: str = ""
    body_len: int = 0
    all_emails: list[str] = field(default_factory=list)
    from_advocacy_tool: bool = False  # cc'd contact@harvestcreek*


def parse_filename(txt_path: Path) -> tuple[str, str, str]:
    """Returns (folder, pdf_basename, submitter_name_from_filename)."""
    name = txt_path.stem  # e.g. hanson__04-10-26 Public Comment - E. Locke - ...
    folder, _, rest = name.partition("__")
    # submitter initial+last is between " - " markers after the date
    # pattern: MM-DD-YY Public Comment - X. Lastname - Subject...
    m = re.match(r"\d{2}-\d{2}-\d{2} Public Comment - ([^-]+?) - ", rest)
    submitter = m.group(1).strip() if m else ""
    return folder, rest, submitter


def extract_headers(text: str) -> dict[str, str]:
    """Parse the leading email-style header block."""
    headers: dict[str, str] = {}
    # Only scan the first ~40 lines to avoid picking up quoted/forwarded headers
    head_region = "\n".join(text.splitlines()[:40])
    for m in HEADER_RE.finditer(head_region):
        key = m.group(1).lower()
        val = m.group(2).strip()
        if key not in headers:
            headers[key] = val
    return headers


def best_sender_email(from_header: str, body: str, html_path: Path) -> str:
    """Pick the most likely submitter email.

    Priority:
    1. Mailto hyperlink whose anchor text matches the From: name (or first
       mailto anchor in the doc if the header is just a name).
    2. Email literal in the From: header text.
    3. Scan body for a non-city, non-advocacy email.
    """
    from_name = re.sub(r"<.*?>", "", from_header).strip().strip(",").lower()

    if html_path.exists():
        html = html_path.read_text(errors="replace")
        mailto_links = MAILTO_LINK_RE.findall(html)
        # Exact match first: anchor text equals the From name
        for email, anchor in mailto_links:
            anchor_clean = anchor.strip().lower()
            if from_name and anchor_clean == from_name:
                return email.lower()
        # Partial match: last-name token overlap
        if from_name:
            last = from_name.split()[-1]
            for email, anchor in mailto_links:
                if last and last in anchor.strip().lower():
                    e = email.lower()
                    if (
                        e not in EXCLUDE_EMAILS
                        and e.split("@", 1)[1] not in CITY_DOMAINS | ADVOCACY_DOMAINS
                    ):
                        return e
        # Fallback: first mailto whose email is not a city/advocacy address
        for email, _anchor in mailto_links:
            e = email.lower()
            if e in EXCLUDE_EMAILS:
                continue
            domain = e.split("@", 1)[1]
            if domain in CITY_DOMAINS or domain in ADVOCACY_DOMAINS:
                continue
            return e

    if m := EMAIL_RE.search(from_header):
        return m.group(0).lower()

    for e in (x.lower() for x in EMAIL_RE.findall(body)):
        if e in EXCLUDE_EMAILS:
            continue
        domain = e.split("@", 1)[1]
        if domain in CITY_DOMAINS or domain in ADVOCACY_DOMAINS:
            continue
        return e
    return ""


def extract_body(text: str) -> str:
    """Return the comment body: text after the header block, before any forwarded chains."""
    lines = text.splitlines()
    # Find first blank line after the last recognised header line
    header_end = 0
    for i, ln in enumerate(lines[:40]):
        if HEADER_RE.match(ln):
            header_end = i
    # Body starts after the next blank line past header_end
    start = header_end + 1
    while start < len(lines) and lines[start].strip():
        start += 1
    while start < len(lines) and not lines[start].strip():
        start += 1

    body_lines = lines[start:]
    body = "\n".join(body_lines)

    # Strip the outlook "CAUTION" banner
    body = re.sub(
        r"CAUTION: This email originated from outside of the organization.*?safe\.\s*",
        "",
        body,
        flags=re.DOTALL,
    )

    # Cut off forwarded/reply chains to keep only the first (top) message body
    cut_patterns = [
        r"\n-{2,}\s*Forwarded message\s*-{2,}",
        r"\nOn .+ wrote:\s*\n",
        r"\nFrom:\s+.+?\nSent:\s+",
    ]
    for pat in cut_patterns:
        m = re.search(pat, body)
        if m:
            body = body[: m.start()]

    # Also strip the "Please note: If you do not wish to have your e-mail..." disclaimer
    body = re.split(r"\nPlease note:\s*If you do not wish", body, maxsplit=1)[0]

    return body.strip()


def process_one(txt_path: Path) -> Comment:
    text = txt_path.read_text(errors="replace")
    folder, basename, file_submitter = parse_filename(txt_path)
    headers = extract_headers(text)

    body = extract_body(text)
    from_hdr = headers.get("from", "")
    html_path = HTML_DIR / (txt_path.stem + ".html")
    sender = best_sender_email(from_hdr, body, html_path)

    # If From header is just a name (no email), use that; else fall back to filename
    from_name = re.sub(r"<.*?>", "", from_hdr).strip().strip(",")
    submitter_name = from_name or file_submitter

    cc = headers.get("cc", "")
    from_tool = any(
        d in cc.lower()
        for d in ("contact@harvestcreekmt.org", "contact@harvestcreek.org")
    )

    all_emails = sorted({e.lower() for e in EMAIL_RE.findall(text)})

    return Comment(
        folder=folder,
        file=basename,
        from_header=from_hdr,
        from_email=sender,
        submitter_name=submitter_name,
        to_header=headers.get("to", ""),
        cc_header=cc,
        subject=headers.get("subject", ""),
        date=headers.get("date", ""),
        body=body,
        body_len=len(body),
        all_emails=all_emails,
        from_advocacy_tool=from_tool,
    )


def main() -> None:
    records = [process_one(p) for p in sorted(TXT_DIR.glob("*.txt"))]
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps([asdict(r) for r in records], indent=2))
    by_folder: dict[str, int] = {}
    for r in records:
        by_folder[r.folder] = by_folder.get(r.folder, 0) + 1
    print(f"wrote {len(records)} records to {OUT_PATH}")
    print(f"by folder: {by_folder}")
    print(
        f"with sender email: {sum(1 for r in records if r.from_email)} / {len(records)}"
    )
    print(
        f"flagged as advocacy-tool submissions: "
        f"{sum(1 for r in records if r.from_advocacy_tool)}"
    )


if __name__ == "__main__":
    main()
