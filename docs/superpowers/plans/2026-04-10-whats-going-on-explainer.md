# "What's Going On" Explainer Page — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers-extended-cc:subagent-driven-development (recommended) or superpowers-extended-cc:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a `/whats-going-on` explainer page that educates neighbors about two rezoning proposals threatening Harvest Creek, motivates action through narrative storytelling and physical-scale visualizations, and funnels visitors to the existing comment generator.

**Architecture:** New Jinja2 template served by a single new FastAPI route. Shares existing CSS design system (extended with explainer-specific styles). Minimal JS — reuses Alpine countdown component, IntersectionObserver scroll animations, and `fallbackCopy()` clipboard helper from existing `app.js`. No new JS file; inline `<script>` for page-specific behavior.

**Tech Stack:** FastAPI, Jinja2, Pico CSS v2, Alpine.js 3.x, vanilla JS, existing design tokens

---

## File Structure

| File | Action | Responsibility |
|------|--------|----------------|
| `app.py` | Modify | Add `GET /whats-going-on` route |
| `templates/whats-going-on.html` | Create | Full explainer page template |
| `static/css/style.css` | Modify | Add explainer-specific CSS + print styles |
| `templates/index.html` | Modify | Add "What's going on?" link in hero section |

---

### Task 1: Add Route and Template Skeleton

**Goal:** Serve a new `/whats-going-on` page with hero section, OG meta tags, and correct head/footer structure matching `index.html`.

**Files:**
- Modify: `app.py:112` (add route after healthz, before index)
- Create: `templates/whats-going-on.html`

**Acceptance Criteria:**
- [ ] `GET /whats-going-on` returns 200 with HTML
- [ ] Page has correct OG meta tags for social sharing
- [ ] Hero renders with countdown timer and CTA button linking to `/`
- [ ] Footer matches `index.html` footer
- [ ] Counter pill shows comment count from server context

**Verify:** `uv run python app.py` → `curl -s http://localhost:5111/whats-going-on | grep -c "og:title"` → `1`

**Steps:**

- [ ] **Step 1: Add route in `app.py`**

Add this route between the `/healthz` and `/` routes:

```python
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
```

- [ ] **Step 2: Create template skeleton `templates/whats-going-on.html`**

```html
<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>What's Going On — Protect Harvest Creek</title>

    <!-- Open Graph -->
    <meta property="og:title" content="What's Going On — Protect Harvest Creek">
    <meta property="og:description" content="Two rezoning proposals threaten our neighborhood. Written comment deadline April 15. Generate yours in 60 seconds.">
    <meta property="og:type" content="website">
    <meta property="og:image" content="/static/og-image.png">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="What's Going On — Protect Harvest Creek">
    <meta name="twitter:description" content="Two rezoning proposals. One neighborhood. Comment deadline April 15.">

    <!-- Favicon -->
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>&#x1f6d1;</text></svg>">

    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Source+Sans+3:wght@400;600;700&display=swap" rel="stylesheet">

    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css">
    <link rel="stylesheet" href="/static/css/style.css?v={{ cache_bust }}">
    <script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
</head>
<body>

    <!-- Hero — "The Un-Explainer" -->
    <header class="hero" role="banner">
        <div class="hero-inner">
            <div class="hero-badge">Bozeman, MT</div>
            <h1>What's<br>Going On?</h1>
            <p class="hero-lead">You don't need to understand zoning to protect your neighborhood. Two city proposals would put high-density, high-rise development right next to Harvest Creek homes. Here's what's happening and what you can do about it.</p>

            <!-- Countdown -->
            <div x-data="countdown()" x-init="start()" class="countdown-bar">
                <span class="countdown-icon">&#9200;</span>
                <span x-show="days > 0"><strong x-text="days"></strong> days left to submit your written comment</span>
                <span x-show="days <= 0 && !expired"><strong x-text="hours"></strong> hrs, <strong x-text="minutes"></strong> min left!</span>
                <span x-show="expired"><strong>Deadline passed</strong> &mdash; Commission comments due Apr 29</span>
            </div>

            <a href="/" class="btn-hero-cta">Write Your Comment &rarr;</a>

            <p class="hero-subtext">Takes about 60 seconds. Keep reading for the full story&nbsp;&darr;</p>

            {% if comment_count > 0 %}
            <div class="counter-pill">
                <span class="counter-num">{{ comment_count }}</span> comment{{ 's' if comment_count != 1 else '' }} generated by your neighbors
            </div>
            {% endif %}
        </div>
    </header>

    <!-- Sticky Section Nav -->
    <nav class="explainer-nav" role="navigation" aria-label="Page sections">
        <div class="explainer-nav-inner">
            <a href="#story">The Story</a>
            <a href="#annexation">Annexation</a>
            <a href="#housing">Housing</a>
            <a href="#road">The Road</a>
            <a href="#act">Take Action</a>
            <a href="#resources">Resources</a>
        </div>
    </nav>

    <main class="container explainer-main">

        <!-- CONTENT SECTIONS GO HERE (Tasks 2-6) -->

    </main>

    <footer>
        <div class="footer-inner">
            <p>This tool helps you draft a comment &mdash; <strong>you</strong> review, edit, and send it from your own email.</p>
            <div class="footer-share">
                <p class="footer-share-heading">Share with your neighbors</p>
                <div class="footer-share-links">
                    <a id="share-fb" href="#" target="_blank" rel="noopener" class="footer-link footer-link-fb">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg>
                        Facebook
                    </a>
                    <a id="share-x" href="#" target="_blank" rel="noopener" class="footer-link footer-link-x">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
                        X / Twitter
                    </a>
                    <a id="share-nd" href="#" target="_blank" rel="noopener" class="footer-link footer-link-nd">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.477 2 2 6.477 2 12s4.477 10 10 10 10-4.477 10-10S17.523 2 12 2zm0 3a3.5 3.5 0 110 7 3.5 3.5 0 010-7zm0 14.5c-2.33 0-4.39-1.18-5.61-2.98C8.53 14.72 13.47 14.72 15.61 16.52A6.98 6.98 0 0112 19.5z"/></svg>
                        Nextdoor
                    </a>
                </div>
            </div>
            <div class="footer-credit">
                Designed and built by Evan (<a href="mailto:me@evanlocke.com">me@evanlocke.com</a>), your neighbor.
            </div>
        </div>
    </footer>

    <script>
    /* Alpine: Countdown (reused from app.js) */
    document.addEventListener('alpine:init', () => {
        Alpine.data('countdown', () => ({
            days: 0, hours: 0, minutes: 0, expired: false,
            start() {
                this.tick();
                setInterval(() => this.tick(), 60000);
            },
            tick() {
                const target = new Date('2026-04-15T23:59:59-06:00');
                const diff = target - Date.now();
                if (diff <= 0) { this.expired = true; return; }
                this.days = Math.floor(diff / 86400000);
                this.hours = Math.floor((diff % 86400000) / 3600000);
                this.minutes = Math.floor((diff % 3600000) / 60000);
            }
        }));
    });

    /* Scroll animations */
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

        /* Smooth scroll for nav links */
        document.querySelectorAll('.explainer-nav a').forEach(a => {
            a.addEventListener('click', (e) => {
                e.preventDefault();
                const target = document.querySelector(a.getAttribute('href'));
                if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            });
        });

        /* Active section tracking */
        const sections = document.querySelectorAll('section[id]');
        const navLinks = document.querySelectorAll('.explainer-nav a');
        const sectionObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    navLinks.forEach(l => l.classList.remove('active'));
                    const link = document.querySelector(`.explainer-nav a[href="#${entry.target.id}"]`);
                    if (link) link.classList.add('active');
                }
            });
        }, { threshold: 0.3, rootMargin: '-80px 0px -60% 0px' });
        sections.forEach(s => sectionObserver.observe(s));

        /* Share link URLs */
        const url = encodeURIComponent(location.href);
        const msg = encodeURIComponent('Two rezoning proposals threaten Harvest Creek. Learn what\'s happening and comment in 60 seconds:');
        const fb = document.getElementById('share-fb');
        const x = document.getElementById('share-x');
        const nd = document.getElementById('share-nd');
        if (fb) fb.href = `https://www.facebook.com/sharer/sharer.php?u=${url}&quote=${msg}`;
        if (x) x.href = `https://twitter.com/intent/tweet?text=${msg}&url=${url}`;
        if (nd) nd.href = `https://nextdoor.com/sharekit/?body=${msg}%20${url}`;
    });

    /* Clipboard helper (works over HTTP) */
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
    </script>
</body>
</html>
```

- [ ] **Step 3: Start dev server and verify skeleton**

Run: `uv run python app.py`
Navigate to: `http://localhost:5111/whats-going-on`
Expected: Hero section renders with countdown, CTA button, counter pill

- [ ] **Step 4: Commit**

```bash
git add app.py templates/whats-going-on.html
git commit -m "feat: add /whats-going-on route and template skeleton"
```

---

### Task 2: Timeline and Overview Content Sections

**Goal:** Add "The Story" timeline section and "Two Proposals, One Neighborhood" overview section with narrative content.

**Files:**
- Modify: `templates/whats-going-on.html` (add sections inside `<main>`)

**Acceptance Criteria:**
- [ ] Timeline section renders with 7 chronological entries (2017 → May 2026)
- [ ] Overview section renders with framing quote and Nina Harrison quote
- [ ] Both sections have `animate-in` classes for scroll animations
- [ ] Sections have correct `id` attributes for anchor navigation

**Verify:** Browser — timeline entries appear with scroll-triggered animations

**Steps:**

- [ ] **Step 1: Add timeline and overview sections inside `<main>`**

Replace the `<!-- CONTENT SECTIONS GO HERE (Tasks 2-6) -->` comment with:

```html
        <!-- The Story — Timeline of Broken Promises -->
        <section id="story" class="explainer-section animate-in">
            <h2 class="section-heading">The Story</h2>
            <p class="section-intro">This isn't just about zoning codes. It's about a pattern of promises made and broken.</p>

            <div class="timeline">
                <div class="timeline-entry">
                    <div class="timeline-year">2017</div>
                    <div class="timeline-content">
                        <strong>City buys the land.</strong> The purchase agreement commits to <em>"preserve existing trees, open spaces and irrigation ditch."</em>
                    </div>
                </div>
                <div class="timeline-entry">
                    <div class="timeline-year">2020–25</div>
                    <div class="timeline-content">
                        <strong>Neighbors invest.</strong> Families buy homes bordering the parcel, trusting the city's commitment. Property values reflect the promise of preserved open space.
                    </div>
                </div>
                <div class="timeline-entry">
                    <div class="timeline-year">Late 2025</div>
                    <div class="timeline-content">
                        <strong>City proposes 84 units at 18 units/acre.</strong> Buildings up to 5 stories. No prior notice to the 18 homeowners whose backyards directly border the parcel.
                    </div>
                </div>
                <div class="timeline-entry">
                    <div class="timeline-year">Jan 2026</div>
                    <div class="timeline-content">
                        <strong>Citizen outcry works.</strong> After months of organized response, the City Commission agrees to a consensus-based engagement process with Harvest Creek HOA.
                    </div>
                </div>
                <div class="timeline-entry">
                    <div class="timeline-year">Mar 2026</div>
                    <div class="timeline-content">
                        <strong>Hanson Lane annexation filed — separately.</strong> This could predetermine R-B zoning for the entire Fowler corridor, undermining the consensus process the city just agreed to.
                    </div>
                </div>
                <div class="timeline-entry timeline-entry-urgent">
                    <div class="timeline-year">Apr 15</div>
                    <div class="timeline-content">
                        <strong>Written comment deadline.</strong> Comments due for the Community Development Board hearing on the annexation.
                    </div>
                </div>
                <div class="timeline-entry timeline-entry-urgent">
                    <div class="timeline-year">Apr 20</div>
                    <div class="timeline-content">
                        <strong>Public hearing.</strong> Community Development Board, 6:00 PM, City Hall (121 N Rouse Ave).
                    </div>
                </div>
                <div class="timeline-entry timeline-entry-urgent">
                    <div class="timeline-year">May 5</div>
                    <div class="timeline-content">
                        <strong>City Commission vote.</strong> Two votes: annexation + zoning. Written comments due April 29.
                    </div>
                </div>
            </div>

            <p class="timeline-coda">See the pattern? <a href="#act">Here's what you can do &rarr;</a></p>
        </section>

        <!-- Two Proposals, One Neighborhood -->
        <section id="overview" class="explainer-section animate-in">
            <h2 class="section-heading">Two Proposals, One Neighborhood</h2>
            <p>Bozeman needs housing. But we don't build 5-story towers in 1-story neighborhoods. Two interconnected proposals would fundamentally change the Fowler Avenue corridor &mdash; and the Harvest Creek neighborhood next to it.</p>
            <blockquote class="neighbor-quote">
                <p>&ldquo;We aren't saying not in our backyard. We aren't saying don't build. We are just asking you to work with us and not approve this high-density plan.&rdquo;</p>
                <cite>&mdash; Nina Harrison, Harvest Creek HOA Subcommittee</cite>
            </blockquote>
            <p>Below are the facts on both proposals, what they mean for your neighborhood, and exactly how to make your voice heard.</p>
        </section>
```

- [ ] **Step 2: Verify in browser**

Refresh `http://localhost:5111/whats-going-on`
Expected: Timeline renders with entries, overview section shows with blockquote

- [ ] **Step 3: Commit**

```bash
git add templates/whats-going-on.html
git commit -m "feat: add timeline and overview content sections"
```

---

### Task 3: Annexation and Housing Issue Sections

**Goal:** Add the two detailed issue sections with facts, scale visualizations, and key date callouts.

**Files:**
- Modify: `templates/whats-going-on.html` (add sections after overview)

**Acceptance Criteria:**
- [ ] Annexation section has: what's proposed, why R-B is wrong, scale viz, precedent, traffic/school safety, what neighbors want, key date callout
- [ ] Housing section has: what's proposed, scale viz, why it's wrong (5 sub-points), promise-vs-reality diff, consensus process, Bridger View model, key date callout
- [ ] Both sections have correct email addresses and `id` anchors
- [ ] Scale comparisons use `.scale-viz` callout boxes

**Verify:** Browser — both issue sections render with all sub-sections and callouts

**Steps:**

- [ ] **Step 1: Add annexation section after overview**

```html
        <!-- Issue 1: Hanson Lane Annexation -->
        <section id="annexation" class="explainer-section animate-in">
            <h2 class="section-heading">Issue 1: Hanson Lane Annexation</h2>
            <span class="issue-badge issue-badge-red">Application 25775 &mdash; Hearing April 20</span>

            <h3>What's Proposed</h3>
            <ul>
                <li>Annexation of an unincorporated parcel between Oak and Durston along the Fowler corridor</li>
                <li>Rezoning to <strong>R-B</strong> (mixed-use residential): 45-foot height max, up to 5 stories</li>
                <li>Extension of Annie Street as a through street into Harvest Creek</li>
                <li>Total developable area: ~5 acres once right-of-way is built</li>
            </ul>

            <div class="scale-viz">
                <div class="scale-viz-label">Putting it in perspective</div>
                <p><strong>5 stories = 45 feet.</strong> That's the height of Bozeman City Hall. Imagine that behind your backyard, separated by a 6-foot fence.</p>
            </div>

            <h3>Why R-B Zoning Is Wrong</h3>
            <p><strong>It's textbook spot zoning.</strong> Surrounding properties are R-1/R-2 single-family homes at &le;6 units/acre. Dropping R-B density into an established low-density area is disfavored under Montana law.</p>
            <p><strong>The Community Plan doesn't require it.</strong> The "Urban Neighborhood" designation is a growth policy statement, not a regulation. R-A zoning satisfies it without R-B intensity.</p>
            <p><strong>The area lacks transit and services.</strong> R-B is designed for areas with good transit and walkable shopping. The closest shopping is over a mile away &mdash; a 30-minute walk each way. No reliable public transit serves this area.</p>

            <h3>The Precedent Problem</h3>
            <p>If R-B is approved here, it sets the stage for R-B zoning on <strong>every parcel</strong> along Fowler between Durston and Oak &mdash; transforming the entire corridor into high-density development directly adjacent to single-family neighborhoods.</p>

            <h3>Traffic &amp; School Safety</h3>
            <p>The annexation extends Annie Street as a through street. Without traffic calming, Annie becomes an unobstructed corridor leading directly to <strong>Emily Dickinson Elementary School</strong> at 2435 Annie Street. Children walk this route daily.</p>

            <h3>What Neighbors Want</h3>
            <p><strong>R-A zoning</strong> (&le;6 units/acre) &mdash; consistent with the surrounding development pattern, the growth policy, and the future land use map. Include this parcel in the existing consensus process rather than approving zoning in isolation.</p>

            <div class="key-date-callout">
                <div class="key-date-icon">&#128197;</div>
                <div>
                    <strong>Community Development Board Hearing</strong><br>
                    April 20, 2026 &mdash; 6:00 PM<br>
                    City Hall, 121 N Rouse Ave, Bozeman<br>
                    <span class="key-date-email">Written comments: <a href="mailto:comments@bozeman.net?subject=Hanson%20Lane%20App%2025775%20Annexation%20and%20Zoning">comments@bozeman.net</a></span>
                </div>
            </div>
        </section>
```

- [ ] **Step 2: Add housing section after annexation**

```html
        <!-- Issue 2: Fowler Housing Development -->
        <section id="housing" class="explainer-section animate-in">
            <h2 class="section-heading">Issue 2: Fowler Housing Development</h2>
            <span class="issue-badge issue-badge-amber">Consensus Process Underway</span>

            <h3>What's Proposed</h3>
            <ul>
                <li>Up to <strong>84 units</strong> at ~18 units/acre with 168 cars</li>
                <li>Buildings up to 4&ndash;5 stories on a city-owned parcel along Fowler Ave (Oak to Annie)</li>
                <li>Unit prices: $450K&ndash;$650K</li>
                <li>Entrances on Farmall and Caterpillar Streets (residential roads), <em>not</em> on Fowler Avenue</li>
            </ul>

            <div class="scale-viz">
                <div class="scale-viz-label">How narrow is the site?</div>
                <p><strong>150 feet wide &mdash; half a football field.</strong> After 35-foot setbacks: 80 feet. After road and driveways: only 30 feet for structures. That's narrower than a two-car garage is long.</p>
            </div>

            <h3>Why the Current Plan Is Wrong</h3>

            <h4>No buffer from existing homes</h4>
            <p>18 homeowners have backyards directly bordering the parcel. Unlike every other R-3 to R-1 transition in Bozeman, there is <em>no roadway buffer</em> between the development and existing backyards. About 50% of surface parking and alleyways would run along property lines.</p>

            <h4>Traffic on residential streets</h4>
            <div class="scale-viz">
                <div class="scale-viz-label">168 new cars</div>
                <p>That's roughly <strong>one car every 35 seconds during rush hour</strong> on Caterpillar and Farmall Streets &mdash; residential roads not designed for this volume. No access is planned from Fowler Avenue itself.</p>
            </div>

            <h4>Not actually affordable</h4>
            <p><strong>$450K&ndash;$650K units don't qualify as affordable housing</strong> by any standard metric. No grants, sponsorships, or nonprofit collaboration (HRDC, Trust Montana) have been announced. Other R-3 affordable developments are already underway elsewhere (160 acres at Baxter/Cottonwood).</p>

            <h4>Inadequate public process</h4>
            <p>The proposal was fast-tracked without sufficient public input. No outreach via mail, email, or door-to-door canvassing to the adjacent homeowners most affected.</p>

            <h4>The broken promise</h4>
            <div class="diff-compare">
                <div class="diff-side diff-promise">
                    <div class="diff-label">2017 Purchase Agreement</div>
                    <p>&ldquo;Preserve existing trees, open spaces and irrigation ditch.&rdquo;</p>
                </div>
                <div class="diff-side diff-reality">
                    <div class="diff-label">2026 Proposal</div>
                    <p>84 units, 4&ndash;5 stories, parking lots and alleyways running along existing backyards.</p>
                </div>
            </div>

            <h3>The Consensus Process</h3>
            <p>On January 6, 2026, after months of citizen outcry, the City Commission invited Harvest Creek HOA to participate in a consensus-based engagement process. Preliminary mediation interviews are underway. Any separate zoning actions &mdash; like the Hanson Lane annexation &mdash; risk undermining this process before it can produce results.</p>

            <h3>What Good Development Looks Like</h3>
            <p><strong>Bridger View</strong> &mdash; just a mile away &mdash; is the model. 1&ndash;2 story homes, 50% greenspace, ADA-compliant, used as a <a href="https://www.minneapolisfed.org/article/2022/what-works-in-housing-affordability-creating-middle-income-housing-with-the-bridger-view-neighborhood" target="_blank" rel="noopener">Federal Reserve case study</a> for successful affordable housing. That's what neighbors are asking for &mdash; not zero development, but <em>right-sized</em> development.</p>

            <p>What neighbors want: max 8 units/acre, 1&ndash;2 stories, at least 50% greenspace, no road connections to Harvest Creek, entrances on Fowler Ave only, and a 3&ndash;5 year planning horizon with secured grants and a consensus process.</p>

            <div class="key-date-callout">
                <div class="key-date-icon">&#128197;</div>
                <div>
                    <strong>Fowler Housing Development</strong><br>
                    Consensus process ongoing &mdash; your written comment still matters<br>
                    <span class="key-date-email">Written comments: <a href="mailto:agenda@bozeman.net?subject=Public%20Comment%20on%20Fowler%20Avenue%20Housing%20Development">agenda@bozeman.net</a></span>
                </div>
            </div>
        </section>
```

- [ ] **Step 3: Verify in browser**

Refresh page. Both issue sections should render with all sub-sections, scale visualizations, diff comparison, and key date callouts.

- [ ] **Step 4: Commit**

```bash
git add templates/whats-going-on.html
git commit -m "feat: add annexation and housing issue detail sections"
```

---

### Task 4: Road Section, Action Section, and Resources

**Goal:** Add the Fowler Avenue road context section, "What You Can Do" action section with pre-crafted share messages, and collapsible resources section.

**Files:**
- Modify: `templates/whats-going-on.html` (add sections after housing)

**Acceptance Criteria:**
- [ ] Road section shows 3-phase construction timeline
- [ ] Action section has 4 steps with CTA buttons and copy-paste share blocks
- [ ] Share blocks copy to clipboard on click with visual feedback
- [ ] Resources section uses `<details>` for collapsible categories
- [ ] Final CTA section with large button linking to `/`

**Verify:** Browser — click "Copy for Nextdoor" → text is in clipboard

**Steps:**

- [ ] **Step 1: Add road, action, resources, and final CTA sections**

```html
        <!-- The Road -->
        <section id="road" class="explainer-section animate-in">
            <h2 class="section-heading">The Road: Fowler Avenue Connector</h2>
            <p>The road project and housing proposals are interdependent. The Fowler Avenue Connection will extend Fowler from Oak Street to Huffine Lane as a 2-lane minor arterial with shared-use paths, a roundabout at Annie/Durston, and a traffic signal at Babcock.</p>

            <div class="road-timeline">
                <div class="road-phase">
                    <div class="road-phase-year">2026</div>
                    <div class="road-phase-detail">
                        <strong>Phase 1:</strong> Oak to Durston<br>Construction begins summer 2026
                    </div>
                </div>
                <div class="road-phase">
                    <div class="road-phase-year">2027</div>
                    <div class="road-phase-detail">
                        <strong>Phase 2:</strong> Durston to Babcock
                    </div>
                </div>
                <div class="road-phase">
                    <div class="road-phase-year">2028</div>
                    <div class="road-phase-detail">
                        <strong>Phase 3:</strong> Babcock to Huffine
                    </div>
                </div>
            </div>

            <p>At the 60% design stage, the Harvest Creek buffer was reduced from 30 feet to 15 feet. Development should be planned in direct coordination with road construction &mdash; not decided in isolation beforehand.</p>
        </section>

        <!-- What You Can Do -->
        <section id="act" class="explainer-section explainer-section-highlight animate-in">
            <h2 class="section-heading">What You Can Do</h2>
            <p class="section-intro">The 3-minute civic workout. Every step counts.</p>

            <div class="action-steps">
                <div class="action-step-item">
                    <div class="action-step-num">1</div>
                    <div class="action-step-body">
                        <h3>Write your comment <span class="action-time">60 seconds</span></h3>
                        <p>Our tool generates a personalized public comment for both proposals. You review it, edit if you want, and send from your own email.</p>
                        <a href="/" class="btn-action-cta">Generate Your Comment &rarr;</a>
                    </div>
                </div>

                <div class="action-step-item">
                    <div class="action-step-num">2</div>
                    <div class="action-step-body">
                        <h3>Share with 3 neighbors <span class="action-time">30 seconds</span></h3>
                        <p>Copy a ready-made message and paste it where your neighbors are.</p>
                        <div class="share-blocks">
                            <div class="share-block" x-data="{ copied: false }">
                                <div class="share-block-label">For Nextdoor / Facebook</div>
                                <div class="share-block-text">The city wants to build 5-story buildings behind Harvest Creek homes. Written comments due April 15. This tool writes your comment in 60 seconds: https://protectharvestcreek.com</div>
                                <button @click="fallbackCopy($el.previousElementSibling.textContent.trim()); copied = true; setTimeout(() => copied = false, 2000)" class="btn-share-copy-sm" :class="copied && 'copied'" x-text="copied ? 'Copied!' : 'Copy'"></button>
                            </div>
                            <div class="share-block" x-data="{ copied: false }">
                                <div class="share-block-label">For text / SMS</div>
                                <div class="share-block-text">Have you seen what they're planning on Fowler Ave? 5-story buildings behind our homes. Comment deadline Apr 15. Takes 60 sec: https://protectharvestcreek.com</div>
                                <button @click="fallbackCopy($el.previousElementSibling.textContent.trim()); copied = true; setTimeout(() => copied = false, 2000)" class="btn-share-copy-sm" :class="copied && 'copied'" x-text="copied ? 'Copied!' : 'Copy'"></button>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="action-step-item">
                    <div class="action-step-num">3</div>
                    <div class="action-step-body">
                        <h3>Mark your calendar <span class="action-time">10 seconds</span></h3>
                        <p>The hearing is <strong>April 20 at 6 PM</strong> at City Hall (121 N Rouse Ave). You can attend in person or submit comments remotely.</p>
                    </div>
                </div>

                <div class="action-step-item">
                    <div class="action-step-num">4</div>
                    <div class="action-step-body">
                        <h3>Show up</h3>
                        <p>There are only 5 City Commissioners. If 3 of them hear from enough neighbors, the zoning proposal fails. Your comment is not symbolic &mdash; it's decisive.</p>
                    </div>
                </div>
            </div>
        </section>

        <!-- Resources -->
        <section id="resources" class="explainer-section animate-in">
            <h2 class="section-heading">Learn More</h2>

            <details class="resource-group" open>
                <summary>Official City Resources</summary>
                <ul class="resource-list">
                    <li><a href="https://engage.bozeman.net/fowler" target="_blank" rel="noopener">Fowler Avenue Connection &mdash; Engage Bozeman</a></li>
                    <li><a href="https://engage.bozeman.net/fowlerhousing" target="_blank" rel="noopener">Fowler Ave Community Housing &mdash; Engage Bozeman</a></li>
                    <li><a href="https://www.bozeman.net/our-city/city-projects/fowler-avenue-connection" target="_blank" rel="noopener">Fowler Avenue Connection &mdash; City of Bozeman</a></li>
                    <li><a href="https://bozeman-community-plan-1-bozeman.hub.arcgis.com/" target="_blank" rel="noopener">Bozeman Community Plan &mdash; Growth Policy &amp; Future Land Use Map</a></li>
                    <li><a href="https://www.arcgis.com/apps/webappviewer/index.html?id=59e315bce7b84d6bbcf22fbd3fa9460b" target="_blank" rel="noopener">Bozeman Interactive Zoning Map</a></li>
                    <li><a href="https://library.municode.com/mt/bozeman/codes/code_of_ordinances?nodeId=PTIICOOR_CH38UNDECO_ART3ZODILAUS" target="_blank" rel="noopener">Bozeman Code of Ordinances &mdash; Zoning Districts</a></li>
                    <li><a href="https://www.bozeman.net/departments/community-development/planning/community-plans-documents-reports" target="_blank" rel="noopener">Community Plans, Documents &amp; Reports</a></li>
                </ul>
            </details>

            <details class="resource-group">
                <summary>News Coverage</summary>
                <ul class="resource-list">
                    <li><a href="https://nbcmontana.com/news/local/bozeman-residents-express-concerns-over-proposed-housing-project" target="_blank" rel="noopener">Residents Express Concerns Over Proposed Housing &mdash; NBC Montana</a></li>
                    <li><a href="https://www.bozemandailychronicle.com/news/bozeman-montana-fowler-avenue-housing/article_b8da3a5a-4733-4eb2-955d-c79101b72af9.html" target="_blank" rel="noopener">Bozeman Eyes New Housing Along Fowler &mdash; Daily Chronicle</a></li>
                    <li><a href="https://www.bozemandailychronicle.com/news/bozeman-affordable-housing-project/article_61aa057a-25d2-4fa7-864e-a61f9d96f3dd.html" target="_blank" rel="noopener">Affordable Housing Proposed for Fowler &mdash; Daily Chronicle</a></li>
                    <li><a href="https://www.kbzk.com/news/local-news/upcoming-fowler-avenue-construction-what-to-expect-resident-thoughts" target="_blank" rel="noopener">Upcoming Construction: What To Expect &mdash; KBZK</a></li>
                    <li><a href="https://montanafreepress.org/2026/04/03/bozeman-housing-market-cools-but-a-stable-market-hasnt-meant-an-affordable-one/" target="_blank" rel="noopener">Bozeman Housing Market Cools &mdash; Montana Free Press</a></li>
                </ul>
            </details>

            <details class="resource-group">
                <summary>The Bridger View Model</summary>
                <ul class="resource-list">
                    <li><a href="http://www.bridgerview.org/" target="_blank" rel="noopener">Bridger View Neighborhood</a></li>
                    <li><a href="https://headwatershousing.org/about/" target="_blank" rel="noopener">Headwaters Community Housing Trust</a></li>
                    <li><a href="https://www.minneapolisfed.org/article/2022/what-works-in-housing-affordability-creating-middle-income-housing-with-the-bridger-view-neighborhood" target="_blank" rel="noopener">Federal Reserve Case Study: Bridger View</a></li>
                    <li><a href="https://www.henneberyeddy.com/project/bridger-view-neighborhood/" target="_blank" rel="noopener">Bridger View Architecture &mdash; Hennebery Eddy</a></li>
                </ul>
            </details>

            <details class="resource-group">
                <summary>Key Contacts</summary>
                <ul class="resource-list">
                    <li><strong>Annexation comments:</strong> <a href="mailto:comments@bozeman.net">comments@bozeman.net</a> (reference "Hanson Lane App 25775")</li>
                    <li><strong>Housing comments:</strong> <a href="mailto:agenda@bozeman.net">agenda@bozeman.net</a> (reference "Fowler Avenue Housing Development")</li>
                    <li><strong>David Fine</strong>, Economic Development Manager: <a href="mailto:dfine@bozeman.net">dfine@bozeman.net</a></li>
                    <li><strong>Nick Ross</strong>, Director of Transportation &amp; Engineering: <a href="mailto:nross@bozeman.net">nross@bozeman.net</a></li>
                </ul>
            </details>
        </section>

        <!-- Final CTA -->
        <section class="explainer-section explainer-cta-final animate-in">
            {% if comment_count > 0 %}
            <div class="counter-pill counter-pill-dark">
                <span class="counter-num">{{ comment_count }}</span> neighbors have already commented
            </div>
            {% endif %}
            <h2>Join them. Write yours.</h2>
            <a href="/" class="btn-hero-cta btn-hero-cta-lg">Generate Your Comment &rarr;</a>
            <p class="cta-subtext">It takes about 60 seconds. You review everything before it's sent.</p>
        </section>
```

- [ ] **Step 2: Verify in browser**

Refresh page. Verify:
- Road section shows 3-phase timeline
- Action section has 4 numbered steps
- Share block copy buttons work (click → "Copied!")
- Resources sections expand/collapse
- Final CTA renders with counter pill and button

- [ ] **Step 3: Commit**

```bash
git add templates/whats-going-on.html
git commit -m "feat: add road, action, resources, and CTA sections"
```

---

### Task 5: Explainer-Specific CSS

**Goal:** Add all CSS needed for the explainer page: sticky nav, timeline, scale visualizations, diff comparison, action steps, share blocks, key date callouts, resource lists, and print styles.

**Files:**
- Modify: `static/css/style.css` (append after `@media (min-width: 769px)` block at line 1067)

**Acceptance Criteria:**
- [ ] Sticky section nav renders and tracks active section on scroll
- [ ] Timeline has left-border visual line with year markers
- [ ] Scale viz callout boxes have amber accent
- [ ] Diff comparison shows side-by-side on desktop, stacked on mobile
- [ ] Action steps have numbered circles and CTA buttons
- [ ] Share blocks have copy buttons with "Copied!" state
- [ ] Resources use styled `<details>` elements
- [ ] Print styles hide nav and produce clean output

**Verify:** Browser — all sections are properly styled, mobile responsive

**Steps:**

- [ ] **Step 1: Append explainer CSS to `style.css`**

Add the following after the closing `}` of the `@media (min-width: 769px)` block (after line 1067):

```css
/* ══ EXPLAINER PAGE ══════════════════════════════════════ */

/* ── Hero CTA Button ─────────────────────────────────── */
.btn-hero-cta {
    display: inline-block;
    padding: 1rem 2.5rem;
    min-height: 52px;
    font-family: var(--font-body);
    font-size: 1.1rem;
    font-weight: 700;
    border-radius: var(--radius-lg);
    background: var(--amber-bright);
    color: white;
    text-decoration: none;
    cursor: pointer;
    transition: all 0.2s cubic-bezier(0.22, 1, 0.36, 1);
    box-shadow: 0 4px 12px rgba(217,119,6,0.25);
    margin-bottom: 0.75rem;
}
.btn-hero-cta:hover {
    background: var(--amber);
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(217,119,6,0.3);
    color: white;
}
.btn-hero-cta-lg {
    font-size: 1.25rem;
    padding: 1.1rem 3rem;
}
.hero-subtext {
    font-size: 0.88rem;
    color: rgba(255,255,255,0.5);
    margin-bottom: 1rem;
}

/* ── Explainer Sticky Nav ────────────────────────────── */
.explainer-nav {
    position: sticky;
    top: 0;
    z-index: 50;
    background: var(--warm-white);
    box-shadow: var(--shadow);
    border-bottom: 1px solid var(--border);
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
}
.explainer-nav-inner {
    display: flex;
    gap: 0;
    max-width: 720px;
    margin: 0 auto;
    padding: 0 1rem;
}
.explainer-nav a {
    display: block;
    padding: 0.85rem 1rem;
    font-size: 0.78rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: var(--text-muted);
    text-decoration: none;
    white-space: nowrap;
    border-bottom: 3px solid transparent;
    transition: all 0.15s ease;
}
.explainer-nav a:hover {
    color: var(--amber);
}
.explainer-nav a.active {
    color: var(--amber);
    border-bottom-color: var(--amber-bright);
}

/* ── Explainer Sections ──────────────────────────────── */
.explainer-main {
    max-width: 720px;
    padding-top: 1.5rem;
}
.explainer-section {
    background: var(--warm-white);
    border-radius: var(--radius-lg);
    padding: 2rem 1.5rem;
    margin-bottom: 1.5rem;
    border: 1px solid var(--border);
    box-shadow: var(--shadow-sm);
    scroll-margin-top: 4.5rem;
}
.explainer-section h3 {
    font-family: var(--font-body);
    font-size: 1.05rem;
    font-weight: 700;
    color: var(--slate-900);
    margin-top: 1.5rem;
    margin-bottom: 0.5rem;
}
.explainer-section h4 {
    font-family: var(--font-body);
    font-size: 0.95rem;
    font-weight: 700;
    color: var(--text-soft);
    margin-top: 1.25rem;
    margin-bottom: 0.35rem;
}
.explainer-section p {
    line-height: 1.7;
    margin-bottom: 0.75rem;
}
.explainer-section ul {
    padding-left: 1.25rem;
    margin-bottom: 1rem;
}
.explainer-section ul li {
    line-height: 1.6;
    margin-bottom: 0.35rem;
}
.section-heading {
    font-family: var(--font-display);
    font-weight: 900;
    font-size: 1.5rem;
    color: var(--slate-900);
    margin: 0 0 0.5rem;
    letter-spacing: -0.01em;
}
.section-intro {
    color: var(--text-soft);
    font-size: 1rem;
    margin-bottom: 1.25rem;
}
.explainer-section-highlight {
    border-color: var(--amber-bright);
    border-width: 2px;
}

/* ── Issue Badges ────────────────────────────────────── */
.issue-badge {
    display: inline-block;
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    padding: 0.3rem 0.75rem;
    border-radius: 2rem;
    margin-bottom: 1rem;
}
.issue-badge-red {
    background: var(--red-light);
    color: var(--red);
    border: 1px solid var(--red);
}
.issue-badge-amber {
    background: var(--amber-light);
    color: var(--amber);
    border: 1px solid var(--amber);
}

/* ── Timeline ────────────────────────────────────────── */
.timeline {
    position: relative;
    padding-left: 1.5rem;
    margin: 1.5rem 0;
    border-left: 3px solid var(--slate-200);
}
.timeline-entry {
    position: relative;
    padding: 0 0 1.5rem 1.25rem;
}
.timeline-entry::before {
    content: '';
    position: absolute;
    left: -1.65rem;
    top: 0.35rem;
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background: var(--slate-300);
    border: 2px solid var(--warm-white);
}
.timeline-entry-urgent::before {
    background: var(--amber-bright);
    box-shadow: 0 0 0 3px var(--amber-light);
}
.timeline-year {
    font-family: var(--font-body);
    font-size: 0.78rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--text-muted);
    margin-bottom: 0.25rem;
}
.timeline-entry-urgent .timeline-year {
    color: var(--amber);
}
.timeline-content {
    font-size: 0.95rem;
    line-height: 1.6;
    color: var(--text);
}
.timeline-content strong {
    color: var(--slate-900);
}
.timeline-coda {
    margin-top: 1rem;
    font-weight: 600;
    color: var(--amber);
}
.timeline-coda a {
    color: var(--amber);
}

/* ── Neighbor Quote ──────────────────────────────────── */
.neighbor-quote {
    border-left: 4px solid var(--amber-bright);
    background: var(--amber-glow);
    padding: 1.25rem 1.5rem;
    margin: 1.25rem 0;
    border-radius: 0 var(--radius) var(--radius) 0;
}
.neighbor-quote p {
    font-style: italic;
    font-size: 1.05rem;
    line-height: 1.6;
    margin-bottom: 0.5rem;
    color: var(--text);
}
.neighbor-quote cite {
    font-size: 0.85rem;
    font-style: normal;
    font-weight: 600;
    color: var(--text-muted);
}

/* ── Scale Visualization ─────────────────────────────── */
.scale-viz {
    background: var(--amber-glow);
    border: 1px solid rgba(217,119,6,0.2);
    border-left: 4px solid var(--amber-bright);
    border-radius: 0 var(--radius) var(--radius) 0;
    padding: 1rem 1.25rem;
    margin: 1rem 0;
}
.scale-viz-label {
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--amber);
    margin-bottom: 0.35rem;
}
.scale-viz p {
    margin: 0;
    font-size: 0.95rem;
    line-height: 1.6;
}

/* ── Diff Comparison ─────────────────────────────────── */
.diff-compare {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
    margin: 1rem 0;
}
.diff-side {
    padding: 1rem;
    border-radius: var(--radius);
}
.diff-promise {
    background: var(--forest-light);
    border: 1px solid var(--forest);
}
.diff-reality {
    background: var(--red-light);
    border: 1px solid var(--red);
}
.diff-label {
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 0.5rem;
}
.diff-promise .diff-label { color: var(--forest); }
.diff-reality .diff-label { color: var(--red); }
.diff-side p {
    margin: 0;
    font-size: 0.92rem;
    line-height: 1.5;
}

/* ── Key Date Callout ────────────────────────────────── */
.key-date-callout {
    display: flex;
    gap: 1rem;
    align-items: flex-start;
    background: var(--amber-glow);
    border: 2px solid var(--amber-bright);
    border-radius: var(--radius-lg);
    padding: 1.25rem;
    margin-top: 1.5rem;
}
.key-date-icon {
    font-size: 1.5rem;
    flex-shrink: 0;
}
.key-date-callout strong {
    color: var(--slate-900);
    font-size: 1rem;
}
.key-date-callout br + span,
.key-date-callout span,
.key-date-callout div {
    font-size: 0.92rem;
    line-height: 1.6;
    color: var(--text-soft);
}
.key-date-email a {
    color: var(--amber);
    font-weight: 600;
}

/* ── Road Timeline ───────────────────────────────────── */
.road-timeline {
    display: flex;
    gap: 1rem;
    margin: 1.5rem 0;
}
.road-phase {
    flex: 1;
    background: var(--slate-100);
    border-radius: var(--radius);
    padding: 1rem;
    border-top: 3px solid var(--slate-300);
}
.road-phase:first-child {
    border-top-color: var(--amber-bright);
}
.road-phase-year {
    font-size: 1.5rem;
    font-weight: 900;
    font-family: var(--font-display);
    color: var(--slate-800);
    margin-bottom: 0.35rem;
}
.road-phase-detail {
    font-size: 0.85rem;
    line-height: 1.5;
    color: var(--text-soft);
}

/* ── Action Steps ────────────────────────────────────── */
.action-steps {
    display: flex;
    flex-direction: column;
    gap: 1.25rem;
}
.action-step-item {
    display: flex;
    gap: 1rem;
    align-items: flex-start;
}
.action-step-num {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    background: var(--amber-bright);
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1rem;
    font-weight: 700;
    flex-shrink: 0;
    margin-top: 0.15rem;
}
.action-step-body h3 {
    margin: 0 0 0.35rem;
    font-size: 1.05rem;
}
.action-step-body p {
    font-size: 0.92rem;
    margin-bottom: 0.75rem;
}
.action-time {
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--text-muted);
    background: var(--slate-100);
    padding: 0.15rem 0.5rem;
    border-radius: 2rem;
    vertical-align: middle;
}
.btn-action-cta {
    display: inline-block;
    padding: 0.75rem 1.75rem;
    font-family: var(--font-body);
    font-size: 0.95rem;
    font-weight: 700;
    border-radius: var(--radius);
    background: var(--amber-bright);
    color: white;
    text-decoration: none;
    transition: all 0.15s ease;
    box-shadow: 0 2px 8px rgba(217,119,6,0.2);
}
.btn-action-cta:hover {
    background: var(--amber);
    transform: translateY(-1px);
    color: white;
}

/* ── Share Blocks ────────────────────────────────────── */
.share-blocks {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}
.share-block {
    position: relative;
    background: var(--warm-bg);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 0.85rem 1rem;
}
.share-block-label {
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--text-muted);
    margin-bottom: 0.35rem;
}
.share-block-text {
    font-size: 0.88rem;
    line-height: 1.5;
    color: var(--text-soft);
    margin-bottom: 0.5rem;
}
.btn-share-copy-sm {
    display: inline-flex;
    align-items: center;
    padding: 0.4rem 1rem;
    min-height: 36px;
    font-family: var(--font-body);
    font-size: 0.8rem;
    font-weight: 600;
    border-radius: var(--radius);
    background: var(--slate-800);
    border: none;
    color: white;
    cursor: pointer;
    transition: all 0.15s ease;
}
.btn-share-copy-sm:hover {
    background: var(--slate-700);
}
.btn-share-copy-sm.copied {
    background: var(--forest);
}

/* ── Resource Groups ─────────────────────────────────── */
.resource-group {
    background: var(--warm-bg);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    margin-bottom: 0.75rem;
}
.resource-group summary {
    padding: 0.85rem 1rem;
    font-size: 0.92rem;
    font-weight: 600;
    color: var(--text);
    cursor: pointer;
    list-style: none;
    display: flex;
    align-items: center;
    gap: 0.4rem;
}
.resource-group summary::before {
    content: '+';
    font-weight: 700;
    font-size: 1rem;
    width: 1.2rem;
    color: var(--text-muted);
    transition: transform 0.2s ease;
}
.resource-group[open] summary::before {
    content: '\2212';
}
.resource-group summary::-webkit-details-marker { display: none; }
.resource-list {
    padding: 0 1rem 0.85rem 2.4rem;
    margin: 0;
}
.resource-list li {
    padding: 0.25rem 0;
    font-size: 0.88rem;
    line-height: 1.5;
}
.resource-list a {
    color: var(--amber);
    text-decoration: none;
}
.resource-list a:hover {
    text-decoration: underline;
}

/* ── Final CTA ───────────────────────────────────────── */
.explainer-cta-final {
    text-align: center;
    border-color: var(--amber-bright);
    border-width: 2px;
    padding: 2.5rem 1.5rem;
}
.explainer-cta-final h2 {
    font-family: var(--font-display);
    font-weight: 900;
    font-size: 1.75rem;
    margin: 0.75rem 0 1rem;
}
.counter-pill-dark {
    background: var(--amber-glow);
    border-color: rgba(217,119,6,0.2);
    color: var(--text-soft);
}
.cta-subtext {
    font-size: 0.88rem;
    color: var(--text-muted);
    margin-top: 0.5rem;
}

/* ── Explainer Responsive ────────────────────────────── */
@media (max-width: 768px) {
    .explainer-section { padding: 1.5rem 1.25rem; }
    .section-heading { font-size: 1.25rem; }
    .diff-compare { grid-template-columns: 1fr; }
    .road-timeline { flex-direction: column; }
    .key-date-callout { flex-direction: column; gap: 0.5rem; }
    .action-step-item { gap: 0.75rem; }
    .explainer-nav-inner { padding: 0 0.5rem; }
    .explainer-nav a { padding: 0.75rem 0.65rem; font-size: 0.7rem; }
    .btn-hero-cta { width: 100%; text-align: center; }
    .btn-hero-cta-lg { font-size: 1.1rem; padding: 1rem 2rem; }
}

/* ── Print Styles ────────────────────────────────────── */
@media print {
    .explainer-nav, .hero, footer, .btn-hero-cta, .btn-action-cta,
    .btn-share-copy-sm, .share-block button { display: none !important; }
    .explainer-section {
        border: none;
        box-shadow: none;
        padding: 1rem 0;
        break-inside: avoid;
    }
    .scale-viz, .key-date-callout, .diff-compare { break-inside: avoid; }
    body { font-size: 11pt; }
    a[href]::after { content: " (" attr(href) ")"; font-size: 0.8em; color: #666; }
    .resource-list a[href]::after { content: none; }
}
```

- [ ] **Step 2: Verify styling in browser**

Refresh page. Check:
- Sticky nav appears and highlights active section on scroll
- Timeline has left-border line with dots
- Scale viz boxes have amber accent
- Diff comparison shows side-by-side
- Resize to mobile width — diff stacks, road phases stack, nav scrolls horizontally

- [ ] **Step 3: Commit**

```bash
git add static/css/style.css
git commit -m "feat: add explainer page CSS with timeline, scale viz, actions, print styles"
```

---

### Task 6: Cross-Link from Main Page

**Goal:** Add a "What's going on?" link in the main page hero so visitors can access the explainer.

**Files:**
- Modify: `templates/index.html:36` (after `hero-lead` paragraph)

**Acceptance Criteria:**
- [ ] "What's going on?" link appears in hero section
- [ ] Link navigates to `/whats-going-on`
- [ ] Styled subtly — doesn't compete with the main CTA

**Verify:** Browser — `/` page shows link in hero; clicking navigates to `/whats-going-on`

**Steps:**

- [ ] **Step 1: Add link in `index.html` hero section**

In `templates/index.html`, after the `<p class="hero-lead">` paragraph (line 36), add:

```html
            <a href="/whats-going-on" class="hero-info-link">What's going on? Read the full story &rarr;</a>
```

- [ ] **Step 2: Add CSS for the link**

In `static/css/style.css`, add after the `.hero-lead` rule (after line 136):

```css
.hero-info-link {
    display: inline-block;
    font-size: 0.88rem;
    color: rgba(255,255,255,0.6);
    text-decoration: none;
    border-bottom: 1px solid rgba(255,255,255,0.2);
    padding-bottom: 1px;
    margin-bottom: 1.25rem;
    transition: all 0.15s ease;
}
.hero-info-link:hover {
    color: var(--amber-bright);
    border-bottom-color: var(--amber-bright);
}
```

- [ ] **Step 3: Verify in browser**

Navigate to `http://localhost:5111/`. Link should appear in hero. Clicking goes to `/whats-going-on`.

- [ ] **Step 4: Commit**

```bash
git add templates/index.html static/css/style.css
git commit -m "feat: add 'What's going on?' link in main page hero"
```

---

## Verification Checklist

1. `uv run python app.py` → both pages load without errors
2. `/whats-going-on` — hero renders with countdown, CTA, counter
3. Sticky nav highlights active section on scroll
4. Timeline tells coherent narrative (2017 → May 2026)
5. Both issue sections have correct facts, scale comparisons, emails, dates
6. Share blocks copy to clipboard with "Copied!" feedback
7. All external links open correctly (spot-check 5-6)
8. Mobile: resize to 375px width — diff stacks, road stacks, nav scrolls
9. OG tags: `curl -s http://localhost:5111/whats-going-on | grep og:title`
10. "What's going on?" link on `/` navigates correctly
11. `Ctrl+P` produces clean printable output (no nav, no buttons)
12. Docker: `just docker-up` → both pages work
