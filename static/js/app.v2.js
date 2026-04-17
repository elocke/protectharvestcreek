/* ── Calendar Events ────────────────────────────────────── */
const EVENTS = [
    { title: 'Comment Deadline: Community Dev Board (noon)', date: '20260420', time: '120000', duration: '0000',
      desc: 'Written comments due by NOON for Community Development Board hearing. Email comments@bozeman.net' },
    { title: 'Community Dev Board Hearing — Hanson Lane Annexation', date: '20260420', time: '180000', duration: '0200',
      desc: 'Hearing at City Hall, 121 N Rouse Ave. In-person & remote oral comments accepted.', location: 'City Hall, 121 N Rouse Ave, Bozeman, MT 59715' },
    { title: 'Comment Deadline: City Commission (Fowler)', date: '20260429', allDay: true,
      desc: 'Written comments due for City Commission re: Hanson Lane App 25775. Email comments@bozeman.net' },
    { title: 'City Commission Vote — Hanson Lane Annexation', date: '20260505', time: '180000', duration: '0200',
      desc: 'Two votes: annexation + zoning. In-person & remote oral comments accepted.', location: 'City Hall, 121 N Rouse Ave, Bozeman, MT 59715' },
];

function downloadIcs(idx) {
    const ev = EVENTS[idx];
    let dtStart, dtEnd;
    if (ev.allDay) {
        dtStart = `DTSTART;VALUE=DATE:${ev.date}`;
        const next = new Date(ev.date.slice(0,4) + '-' + ev.date.slice(4,6) + '-' + ev.date.slice(6,8));
        next.setDate(next.getDate() + 1);
        const nd = next.toISOString().slice(0,10).replace(/-/g, '');
        dtEnd = `DTEND;VALUE=DATE:${nd}`;
    } else {
        dtStart = `DTSTART;TZID=America/Denver:${ev.date}T${ev.time}`;
        const h = parseInt(ev.time.slice(0,2)) + parseInt(ev.duration.slice(0,2));
        dtEnd = `DTEND;TZID=America/Denver:${ev.date}T${String(h).padStart(2,'0')}${ev.time.slice(2)}`;
    }
    const ics = [
        'BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//ProtectHarvestCreek//EN',
        'BEGIN:VEVENT', dtStart, dtEnd,
        `SUMMARY:${ev.title}`, `DESCRIPTION:${ev.desc}`,
        ev.location ? `LOCATION:${ev.location}` : '',
        `UID:${ev.date}-${idx}@protectharvestcreek.com`,
        'END:VEVENT', 'END:VCALENDAR'
    ].filter(Boolean).join('\r\n');
    const blob = new Blob([ics], { type: 'text/calendar' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = ev.title.replace(/[^a-zA-Z0-9]/g, '_') + '.ics';
    a.click();
    URL.revokeObjectURL(a.href);
}

/* ── Alpine: Countdown Timer ───────────────────────────── */
document.addEventListener('alpine:init', () => {
    Alpine.data('countdown', () => ({
        days: 0, hours: 0, minutes: 0, expired: false,
        start() {
            this.tick();
            setInterval(() => this.tick(), 60000);
        },
        tick() {
            const target = new Date('2026-04-20T12:00:00-06:00');
            const diff = target - Date.now();
            if (diff <= 0) { this.expired = true; return; }
            this.days = Math.floor(diff / 86400000);
            this.hours = Math.floor((diff % 86400000) / 3600000);
            this.minutes = Math.floor((diff % 3600000) / 60000);
        }
    }));

    Alpine.data('progressTracker', () => ({
        current: 1,
        _override: 0,
        init() {
            window._progressTracker = this;
            const form = document.getElementById('comment-form');
            if (form) {
                form.addEventListener('input', () => this.update());
                form.addEventListener('change', () => this.update());
            }
        },
        advance(step) {
            this._override = step;
            this.current = step;
        },
        update() {
            if (this._override >= 5) return;
            const steps = document.querySelectorAll('.step[data-step]');
            let max = 1;
            steps.forEach(step => {
                const n = parseInt(step.dataset.step);
                const inputs = step.querySelectorAll('input, textarea');
                let filled = false;
                inputs.forEach(input => {
                    if (input.type === 'checkbox' || input.type === 'radio') {
                        if (input.checked && !input.defaultChecked) filled = true;
                    } else if (input.value.trim()) filled = true;
                });
                if (filled && n >= max) max = n;
            });
            this.current = Math.max(max, this._override);
        }
    }));

    Alpine.data('shareWidget', () => ({
        visible: false,
        linkCopied: false,
        canShare: !!navigator.share,
        shareText: "I just submitted a public comment to help protect Harvest Creek from the Fowler Ave rezoning. You can generate yours in 60 seconds:",
        get smsHref() {
            const body = `${this.shareText} ${location.href}`;
            return `sms:?body=${encodeURIComponent(body)}`;
        },
        get emailHref() {
            const subject = "Protect Harvest Creek — Add your voice";
            const body = `${this.shareText}\n\n${location.href}`;
            return `mailto:?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
        },
        show() { this.visible = true; },
        shareNative() {
            navigator.share({ title: 'Protect Harvest Creek', text: this.shareText, url: location.href });
        },
        copyLink() {
            navigator.clipboard.writeText(location.href).then(() => {
                this.linkCopied = true;
                setTimeout(() => this.linkCopied = false, 2500);
            });
        }
    }));
});

/* ── Scroll Animations ─────────────────────────────────── */
const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('visible');
            observer.unobserve(entry.target);
        }
    });
}, { threshold: 0.1 });

document.addEventListener('DOMContentLoaded', () => {
    window.scrollTo(0, 0);

    document.querySelectorAll('.animate-in').forEach(el => observer.observe(el));

    const url = encodeURIComponent(location.href);
    const msg = encodeURIComponent('Help protect Harvest Creek from the Fowler Ave rezoning in Bozeman. Generate a public comment in 60 seconds:');
    const fb = document.getElementById('share-fb');
    const x = document.getElementById('share-x');
    const nd = document.getElementById('share-nd');
    if (fb) fb.href = `https://www.facebook.com/sharer/sharer.php?u=${url}`;
    if (x) x.href = `https://twitter.com/intent/tweet?text=${msg}&url=${url}`;
    if (nd) nd.href = `https://nextdoor.com/sharekit/?body=${msg}%20${url}`;
});

/* ── Confetti ──────────────────────────────────────────── */
function fireConfetti() {
    const canvas = document.getElementById('confetti-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    const pieces = [];
    const colors = ['#2563eb', '#16a34a', '#f59e0b', '#dc2626', '#8b5cf6', '#ec4899'];
    for (let i = 0; i < 150; i++) {
        pieces.push({
            x: Math.random() * canvas.width,
            y: -20 - Math.random() * 200,
            w: 6 + Math.random() * 6,
            h: 10 + Math.random() * 8,
            color: colors[Math.floor(Math.random() * colors.length)],
            vx: (Math.random() - 0.5) * 4,
            vy: 2 + Math.random() * 4,
            rot: Math.random() * 360,
            rotV: (Math.random() - 0.5) * 10,
            opacity: 1,
        });
    }

    let frame = 0;
    function draw() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        let alive = false;
        pieces.forEach(p => {
            if (p.opacity <= 0) return;
            alive = true;
            ctx.save();
            ctx.translate(p.x, p.y);
            ctx.rotate(p.rot * Math.PI / 180);
            ctx.globalAlpha = p.opacity;
            ctx.fillStyle = p.color;
            ctx.fillRect(-p.w / 2, -p.h / 2, p.w, p.h);
            ctx.restore();
            p.x += p.vx;
            p.y += p.vy;
            p.vy += 0.1;
            p.rot += p.rotV;
            if (frame > 60) p.opacity -= 0.015;
        });
        frame++;
        if (alive) requestAnimationFrame(draw);
        else ctx.clearRect(0, 0, canvas.width, canvas.height);
    }
    draw();
}

/* ── Form Submission + SSE Streaming ───────────────────── */
async function handleSubmit() {
    const form = document.getElementById('comment-form');
    const btn = document.getElementById('submit-btn');
    const resultArea = document.getElementById('result-area');

    btn.disabled = true;
    btn.textContent = 'Writing both comments...';
    resultArea.innerHTML = `
        <div class="step" style="margin-top: 1rem; border-color: var(--accent);">
            <div class="loading-bar"><div class="loading-bar-fill"></div></div>
            <p class="loading-heading">Writing <strong>2 separate comments</strong> for you &mdash; one for each issue</p>
            <div id="stream-text" class="comment-box typing-cursor" style="min-height: 80px; color: #334155;"></div>
            <p class="loading-subhint">You'll send comment 1 of 2 (Annexation), then comment 2 of 2 (Fowler Housing). Takes ~20 seconds total.</p>
        </div>`;
    resultArea.scrollIntoView({ behavior: 'smooth' });

    const formData = new FormData(form);
    const streamEl = document.getElementById('stream-text');
    let fullText = '';

    try {
        const response = await fetch('/generate', { method: 'POST', body: formData });
        if (!response.ok) {
            const err = await response.json().catch(() => null);
            showError(err?.error || 'Something went wrong. Please try again.');
            return;
        }
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop();
            for (const line of lines) {
                if (!line.startsWith('data: ')) continue;
                try {
                    const data = JSON.parse(line.slice(6));
                    if (data.error) { showError(data.error); return; }
                    if (data.text) {
                        fullText += data.text;
                        if (streamEl) streamEl.textContent = fullText.replace(/===COMMENT_SPLIT===/g, '\n---\n');
                    }
                    if (data.done) {
                        showDualResult(data.annexation, data.housing, data.count);
                        return;
                    }
                } catch(_) {}
            }
        }
        if (fullText) showError('Stream ended unexpectedly. Please try again.');
        else showError('No response received. Please try again.');
    } catch (err) {
        showError('Connection error: ' + err.message);
    } finally {
        btn.disabled = false;
        btn.textContent = 'Generate Both Comments';
    }
}

/* ── Result Cards ──────────────────────────────────────── */
function makeCommentCard(text, issueKey, cardId, nextCardId) {
    const issue = window.ISSUES[issueKey];
    const words = text.trim().split(/\s+/).length;
    const color = issueKey === 'annexation' ? 'var(--red)' : 'var(--forest)';
    const icon = issueKey === 'annexation' ? '&#9888;&#65039;' : '&#127960;&#65039;';
    const stepNum = issueKey === 'annexation' ? '1' : '2';
    const totalCards = Object.keys(window.ISSUES).length;

    return `
        <div id="${cardId}" class="result-card animate-in visible" style="margin-top: 1rem; border-color: ${color};"
             x-data="cardFlow('${cardId}', '${issueKey}', '${nextCardId || ''}')">

            <div class="result-badge">Comment ${stepNum} of ${totalCards}</div>
            <div class="result-header">
                <span class="result-icon">${icon}</span>
                <h2 style="color: ${color};">${issue.label}</h2>
            </div>
            <p class="result-meta">
                Send to <strong>${issue.email}</strong> &middot; Click text to edit before sending
            </p>

            <div id="${cardId}-text" contenteditable="true" class="comment-box">${escapeHtml(text)}</div>
            <div class="word-count"><span id="${cardId}-wc">${words}</span> words</div>

            <!-- State: ready -->
            <div class="action-flow" x-show="state === 'ready'">
                <!-- Mobile: step 1 = copy, step 2 = real <a> mailto link -->
                <div x-show="isMobile">
                    <div class="email-steps-guide">
                        <p class="email-steps-title">Here's how sending works:</p>
                        <ol class="email-steps-list">
                            <li>Tap <strong>Copy Comment</strong> below</li>
                            <li>Tap <strong>Open Email App</strong> — address &amp; subject are filled in</li>
                            <li><strong>Paste</strong> your comment and hit send</li>
                        </ol>
                    </div>
                    <button @click="copyComment()" class="btn-action-primary" style="--btn-color: ${color};">
                        Step 1: Copy Comment
                    </button>
                </div>
                <!-- Desktop: copy first, then pick provider -->
                <button x-show="!isMobile" @click="copyComment()" class="btn-action-primary" style="--btn-color: ${color};">
                    Copy Comment to Clipboard
                </button>
                <p x-show="!isMobile" class="action-hint">Then choose your email app to send it</p>
            </div>

            <!-- State: copied (mobile) — show real tappable mailto link -->
            <div class="action-flow" x-show="state === 'copied' && isMobile" x-transition>
                <div class="action-success-banner">
                    <span class="action-check">&#10003;</span>
                    Comment copied!
                </div>
                <a :href="mailtoHref" class="btn-action-primary" style="--btn-color: ${color}; display: block; text-align: center; text-decoration: none; margin-top: 0.75rem;">
                    Step 2: Open Email App
                </a>
                <div class="action-paste-hint" style="margin-top: 0.5rem;">
                    Tap the button above, then <strong>paste</strong> your comment into the email body.
                </div>

                <!-- Fallback for browsers without a default mail handler (e.g. Orion on iOS). -->
                <details class="action-manual-fallback">
                    <summary>Can't open your email app? Tap for manual details &rarr;</summary>
                    <div class="manual-field">
                        <span class="manual-label">To</span>
                        <code class="manual-value">${issue.email}</code>
                        <button type="button" @click="copyAddress('${issue.email}')" class="manual-copy-btn" x-text="toCopied ? 'Copied ✓' : 'Copy'"></button>
                    </div>
                    <div class="manual-field">
                        <span class="manual-label">Cc</span>
                        <code class="manual-value">contact@harvestcreekmt.org</code>
                        <button type="button" @click="copyAddress('contact@harvestcreekmt.org', 'cc')" class="manual-copy-btn" x-text="ccCopied ? 'Copied ✓' : 'Copy'"></button>
                    </div>
                    <div class="manual-field">
                        <span class="manual-label">Subject</span>
                        <code class="manual-value">${escapeHtml(issue.subject)}</code>
                    </div>
                    <p class="manual-hint">Open your email app manually, paste your comment, then send.</p>
                </details>

                <div class="action-row-split">
                    <button @click="markSent()" class="btn-action-done">
                        I sent it${nextCardId ? ' &rarr; Next comment' : ''}
                    </button>
                    <button @click="retryCopy()" class="btn-action-retry">
                        Re-copy
                    </button>
                </div>
            </div>

            <!-- State: copied (desktop) — provider picker -->
            <div class="action-flow" x-show="state === 'copied' && !isMobile" x-transition>
                <div class="action-success-banner">
                    <span class="action-check">&#10003;</span>
                    Copied to clipboard!
                </div>

                <div class="action-truncation-notice">
                    <strong>Heads up:</strong> long comments sometimes get cut off when we pre-fill the email.
                    Your comment is already on your clipboard &mdash; if the body looks short or empty, just paste it in.
                </div>

                <div class="email-picker">
                    <p class="email-picker-label">Pick your email &mdash; we'll pre-fill everything:</p>
                    <div class="email-picker-grid">
                        <button @click="openProvider('gmail')" class="email-picker-btn email-gmail">
                            <svg viewBox="0 0 24 24" width="20" height="20" fill="none"><path d="M22 6c0-1.1-.9-2-2-2H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6zm-2 0l-8 5-8-5h16zm0 12H4V8l8 5 8-5v10z" fill="currentColor"/></svg>
                            Gmail
                        </button>
                        <button @click="openProvider('outlook')" class="email-picker-btn email-outlook">
                            <svg viewBox="0 0 24 24" width="20" height="20" fill="none"><path d="M22 6c0-1.1-.9-2-2-2H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6zm-2 0l-8 5-8-5h16zm0 12H4V8l8 5 8-5v10z" fill="currentColor"/></svg>
                            Outlook
                        </button>
                        <button @click="openProvider('yahoo')" class="email-picker-btn email-yahoo">
                            <svg viewBox="0 0 24 24" width="20" height="20" fill="none"><path d="M22 6c0-1.1-.9-2-2-2H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6zm-2 0l-8 5-8-5h16zm0 12H4V8l8 5 8-5v10z" fill="currentColor"/></svg>
                            Yahoo
                        </button>
                        <button @click="openProvider('other')" class="email-picker-btn email-other">
                            <svg viewBox="0 0 24 24" width="20" height="20" fill="none"><path d="M22 6c0-1.1-.9-2-2-2H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6zm-2 0l-8 5-8-5h16zm0 12H4V8l8 5 8-5v10z" fill="currentColor"/></svg>
                            Other
                        </button>
                    </div>
                </div>

                <button @click="retryCopy()" class="btn-action-retry" style="margin-top: 0.5rem; width: 100%; text-align: center;">
                    Copy again
                </button>
            </div>

            <!-- State: pasting (desktop only) — email is open -->
            <div class="action-flow" x-show="state === 'pasting'" x-transition>
                <div class="action-success-banner">
                    <span class="action-check">&#10003;</span>
                    Email opened with your comment!
                </div>
                <div class="action-paste-hint">
                    Review your comment in the email, then hit <strong>Send</strong>.
                    Body missing or cut off? Tap <strong>Copy body</strong> and paste.
                </div>
                <div class="action-row-split">
                    <button @click="markSent()" class="btn-action-done">
                        I sent it${nextCardId ? ' &rarr; Next comment' : ''}
                    </button>
                    <button @click="retryCopy()" class="btn-action-retry" x-text="bodyCopied ? 'Body copied ✓' : 'Copy body'"></button>
                    <button @click="openProvider(lastProvider)" class="btn-action-retry">
                        Re-open email
                    </button>
                </div>
            </div>

            <!-- State: sent -->
            <div class="action-flow" x-show="state === 'sent'" x-transition>
                <div class="action-sent-banner">
                    <span class="action-check-big">&#10003;</span>
                    Sent! Thank you for speaking up.
                </div>
            </div>
        </div>`;
}

/* ── Clipboard helper (works over HTTP) ──────────────── */
function fallbackCopy(text) {
    if (navigator.clipboard) return navigator.clipboard.writeText(text);
    const ta = document.createElement('textarea');
    ta.value = text;
    ta.style.position = 'fixed';
    ta.style.opacity = '0';
    document.body.appendChild(ta);
    ta.select();
    document.execCommand('copy');
    document.body.removeChild(ta);
    return Promise.resolve();
}

/* ── Card Flow Alpine Component ───────────────────────── */
document.addEventListener('alpine:init', () => {
    Alpine.data('cardFlow', (cardId, issueKey, nextCardId) => ({
        state: 'ready',
        lastProvider: 'gmail',
        bodyCopied: false,
        toCopied: false,
        ccCopied: false,
        isMobile: window.matchMedia('(pointer: coarse)').matches,
        get mailtoHref() {
            const issue = window.ISSUES[issueKey];
            return `mailto:${issue.email}?cc=${encodeURIComponent('contact@harvestcreekmt.org')}&subject=${encodeURIComponent(issue.subject)}`;
        },
        copyText() {
            const el = document.getElementById(cardId + '-text');
            return el ? el.innerText : '';
        },
        copyComment() {
            fallbackCopy(this.copyText()).then(() => {
                this.state = 'copied';
            });
        },
        openProvider(provider) {
            const issue = window.ISSUES[issueKey];
            const body = this.copyText();
            // Re-copy body to clipboard right before opening so paste works even
            // if the webmail/mailto URL gets truncated by the client.
            fallbackCopy(body);
            const to = encodeURIComponent(issue.email);
            const subject = encodeURIComponent(issue.subject);
            const bodyEnc = encodeURIComponent(body);
            const cc = encodeURIComponent('contact@harvestcreekmt.org');
            // Ordering matters: cc before body so if the URL is truncated by the
            // client's length limit, the CC survives. Long comment bodies can push
            // total URL length past the ~2kb mailto limit in some clients.
            let url;
            if (provider === 'gmail') {
                url = `https://mail.google.com/mail/?view=cm&to=${to}&cc=${cc}&su=${subject}&body=${bodyEnc}`;
            } else if (provider === 'outlook') {
                url = `https://outlook.live.com/mail/0/deeplink/compose?to=${to}&cc=${cc}&subject=${subject}&body=${bodyEnc}`;
            } else if (provider === 'yahoo') {
                url = `https://compose.mail.yahoo.com/?to=${to}&cc=${cc}&subject=${subject}&body=${bodyEnc}`;
            } else {
                url = `mailto:${issue.email}?cc=contact@harvestcreekmt.org&subject=${subject}&body=${bodyEnc}`;
            }
            this.lastProvider = provider;
            this.state = 'pasting';
            window.open(url, '_blank');
        },
        retryCopy() {
            fallbackCopy(this.copyText()).then(() => {
                if (this.state === 'pasting') {
                    this.bodyCopied = true;
                    setTimeout(() => { this.bodyCopied = false; }, 2500);
                } else {
                    this.state = 'copied';
                }
            });
        },
        markSent() {
            this.state = 'sent';
            markCardSent(issueKey, nextCardId);
        },
        copyAddress(addr, which) {
            fallbackCopy(addr).then(() => {
                const key = which === 'cc' ? 'ccCopied' : 'toCopied';
                this[key] = true;
                setTimeout(() => { this[key] = false; }, 2000);
            });
        }
    }));
});

/* ── Track sends & scroll to next ─────────────────────── */
function showNextCommentBanner(nextEl) {
    let banner = document.getElementById('next-comment-banner');
    if (!banner) {
        banner = document.createElement('button');
        banner.id = 'next-comment-banner';
        banner.className = 'next-comment-banner';
        banner.type = 'button';
        banner.textContent = '\u2193 Send Comment 2 of 2 (Fowler Housing)';
        banner.addEventListener('click', () => {
            nextEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
        });
        document.body.appendChild(banner);
    }
    requestAnimationFrame(() => banner.classList.add('visible'));
}
function hideNextCommentBanner() {
    const banner = document.getElementById('next-comment-banner');
    if (banner) banner.remove();
}

const emailsSent = new Set();
function markCardSent(issueKey, nextCardId) {
    emailsSent.add(issueKey);

    if (nextCardId) {
        const nextEl = document.getElementById(nextCardId);
        if (nextEl) {
            setTimeout(() => {
                nextEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
                nextEl.classList.add('result-card-highlight');
                setTimeout(() => nextEl.classList.remove('result-card-highlight'), 2000);
            }, 400);
            showNextCommentBanner(nextEl);
        }
        return;
    }

    hideNextCommentBanner();

    if (window._progressTracker) window._progressTracker.advance(6);
    setTimeout(() => {
        fireConfetti();
        const shareSection = document.getElementById('share-section');
        if (shareSection) {
            shareSection.style.display = '';
            const data = shareSection._x_dataStack && shareSection._x_dataStack[0];
            if (data) data.show();
        }
        const contactSection = document.getElementById('contact-hoa-section');
        if (contactSection) contactSection.style.display = '';
        const target = contactSection || shareSection;
        if (target) target.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }, 400);
}

function showDualResult(annexationText, housingText, count) {
    const resultArea = document.getElementById('result-area');
    const btn = document.getElementById('submit-btn');
    btn.disabled = false;
    btn.textContent = 'Generate Both Comments';
    hideNextCommentBanner();

    const hasAnnex = !!annexationText;
    const hasHousing = !!housingText;

    let html = `
        <div class="ai-disclaimer">
            <strong>Please review before sending.</strong> Comments are generated using AI.
            Neither this website nor the Harvest Creek HOA is responsible for their content.
            This website is not affiliated with the Harvest Creek HOA.
        </div>`;
    if (hasAnnex) html += makeCommentCard(annexationText, 'annexation', 'card-annex', hasHousing ? 'card-housing' : '');
    if (hasHousing) html += makeCommentCard(housingText, 'housing', 'card-housing', '');

    html += `
        <div class="regen-row">
            <button onclick="document.getElementById('comment-form').requestSubmit()" class="btn-regen">
                &#8634; Generate New Versions
            </button>
        </div>`;

    if (count) html += `<p class="result-count">${count} comments generated by neighbors so far</p>`;

    resultArea.innerHTML = html;
    resultArea.scrollIntoView({ behavior: 'smooth' });
    if (window._progressTracker) window._progressTracker.advance(5);

    ['card-annex', 'card-housing'].forEach(id => {
        const el = document.getElementById(id + '-text');
        if (el) el.addEventListener('input', () => {
            const wc = document.getElementById(id + '-wc');
            if (wc) wc.textContent = el.innerText.trim().split(/\s+/).length;
        });
    });
}

function showError(msg) {
    const resultArea = document.getElementById('result-area');
    const btn = document.getElementById('submit-btn');
    btn.disabled = false;
    btn.textContent = 'Generate Both Comments';
    resultArea.innerHTML = `
        <div class="step" style="margin-top: 1rem; border-color: #ef4444;">
            <p style="color: #ef4444; font-weight: 600;">Something went wrong</p>
            <p style="color: #64748b;">${escapeHtml(msg)}</p>
            <button onclick="this.closest('.step').remove()" class="btn-regen" style="margin-top: 0.5rem;">Dismiss</button>
        </div>`;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
