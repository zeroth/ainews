#!/usr/bin/env python3
"""
Daily News Bulletin - Static Site Generator
Reads markdown files from content/ and generates a static site in docs/
styled as 'Brief & Co.' (Warm Magazine theme from the design handoff).
"""

import html
import json
import re
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
CONTENT_DIR = SCRIPT_DIR / "content"
DOCS_DIR = SCRIPT_DIR / "docs"
EDITIONS_FILE = SCRIPT_DIR / "editions.json"

FETCH_TIME_LABEL = "07:00"


def slugify(text: str) -> str:
    """Stable, ASCII-only slug for in-page anchors."""
    s = re.sub(r"[^\w\s-]", "", text or "", flags=re.ASCII).strip().lower()
    return re.sub(r"[\s_]+", "-", s) or "section"


def format_long_date(dt: datetime) -> str:
    """Cross-platform '%A, %B %-d, %Y' (Linux %-d isn't portable)."""
    return f"{dt:%A, %B} {dt.day}, {dt:%Y}"


def load_editions() -> dict:
    if EDITIONS_FILE.exists():
        try:
            return json.loads(EDITIONS_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_editions(editions: dict) -> None:
    EDITIONS_FILE.write_text(
        json.dumps(editions, indent=2, sort_keys=True), encoding="utf-8"
    )


def assign_editions(date_dirs: list) -> dict:
    """Persisted date→edition mapping. New dates get max+1; existing keep their number."""
    editions = load_editions()
    next_n = max(editions.values(), default=0) + 1
    for date_str in sorted(date_dirs):
        if date_str not in editions:
            editions[date_str] = next_n
            next_n += 1
    save_editions(editions)
    return editions

# ── CSS — Warm Magazine theme (Brief & Co.) ─────────────────────────────
BASE_CSS = """
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=Work+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
  --bg: #1e1712;
  --surface: #261d17;
  --surface-hi: #2f241c;
  --fg: #f5e8d3;
  --fg-muted: #c0a890;
  --fg-subtle: #8a7866;
  --accent: #e87a4a;
  --accent-2: #8ab070;
  --border: rgba(255,220,180,0.12);
  --divider: rgba(255,220,180,0.1);
  --radius: 4px;
}

* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; min-height: 100vh; }
body {
  background: var(--bg);
  color: var(--fg);
  font-family: 'Work Sans', system-ui, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  line-height: 1.55;
}
a { color: inherit; text-decoration: none; }
::selection { background: rgba(176,74,38,0.25); }

.shell { max-width: 1200px; margin: 0 auto; padding: 0 40px; }

/* ── Masthead ───────────────────────────────────────────────────────── */
.masthead { padding: 40px 0 24px; }
.eyebrow {
  font-family: 'JetBrains Mono', monospace;
  font-size: 10.5px;
  letter-spacing: 0.35em;
  text-transform: uppercase;
  color: var(--accent);
  text-align: center;
  margin-bottom: 14px;
}
.title {
  font-family: 'DM Serif Display', serif;
  font-weight: 400;
  font-size: clamp(60px, 8vw, 110px);
  line-height: 0.92;
  letter-spacing: -0.025em;
  text-align: center;
  margin: 0;
  color: var(--fg);
}
.title .amp {
  color: var(--accent);
  font-style: italic;
}
.dateline {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 18px;
  margin-top: 14px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--fg-muted);
}
.dateline .sep { color: var(--fg-subtle); }

.section-rule {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-top: 32px;
}
.section-rule .bar {
  flex: 1;
  height: 2px;
  background: var(--fg);
}
.section-rule .links {
  display: flex;
  gap: 20px;
  font-family: 'Work Sans', sans-serif;
  font-weight: 600;
  font-size: 12px;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--fg);
  flex-wrap: wrap;
  justify-content: center;
}

.subnav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 22px;
  gap: 16px;
  flex-wrap: wrap;
}
.tabs { display: flex; gap: 8px; }
.tab {
  padding: 8px 18px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  background: transparent;
  color: var(--fg);
  border: 1.5px solid var(--fg);
  border-radius: var(--radius);
  font-weight: 600;
  cursor: pointer;
  display: inline-block;
}
.tab.active {
  background: var(--accent);
  color: var(--surface);
  border-color: var(--accent);
}
.stats {
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: var(--fg-muted);
}

/* ── Hero / cover story ─────────────────────────────────────────────── */
.hero {
  margin-top: 28px;
  padding: 36px 0 44px;
  border-top: 2px solid var(--fg);
  border-bottom: 1px solid var(--divider);
}
.hero-tag {
  display: inline-block;
  padding: 5px 12px;
  background: var(--accent);
  color: var(--surface);
  font-family: 'JetBrains Mono', monospace;
  font-size: 10.5px;
  letter-spacing: 0.22em;
  text-transform: uppercase;
  margin-bottom: 18px;
  font-weight: 600;
}
.hero h2 {
  font-family: 'DM Serif Display', serif;
  font-weight: 400;
  font-size: clamp(40px, 4.5vw, 64px);
  line-height: 1.02;
  letter-spacing: -0.02em;
  color: var(--fg);
  margin: 0 0 22px;
  text-wrap: balance;
}
.hero h2 a:hover { color: var(--accent); }
.hero .summary {
  font-family: 'Work Sans', sans-serif;
  font-size: 17px;
  line-height: 1.6;
  color: var(--fg-muted);
  margin: 0 0 24px;
  font-style: italic;
  text-wrap: pretty;
}
.hero-foot {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 20px;
  border-top: 1px solid var(--divider);
  flex-wrap: wrap;
  gap: 12px;
}
.read-link {
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--accent);
  font-weight: 600;
}
.read-link:hover { color: var(--fg); }

/* ── Section block ──────────────────────────────────────────────────── */
.section-block {
  padding: 44px 0;
  border-bottom: 1px solid var(--divider);
}
.section-head {
  display: flex;
  align-items: baseline;
  gap: 20px;
  margin-bottom: 28px;
}
.section-head .glyph {
  font-family: 'DM Serif Display', serif;
  font-size: 40px;
  color: var(--accent);
  line-height: 1;
}
.section-head h3 {
  font-family: 'DM Serif Display', serif;
  font-weight: 400;
  font-size: 34px;
  line-height: 1.1;
  margin: 0;
  letter-spacing: -0.01em;
  color: var(--fg);
  flex: 1;
}
.section-head .count {
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  letter-spacing: 0.2em;
  color: var(--fg-subtle);
  text-transform: uppercase;
}

.section-grid { display: grid; gap: 40px; }
.section-grid.cols-1 { grid-template-columns: 1fr; }
.section-grid.cols-2 { grid-template-columns: 1fr 1fr; }

.article h4 {
  font-family: 'DM Serif Display', serif;
  font-weight: 400;
  font-size: 22px;
  line-height: 1.2;
  letter-spacing: -0.01em;
  color: var(--fg);
  margin: 0 0 10px;
  text-wrap: balance;
}
.article h4 a:hover { color: var(--accent); }
.article p {
  font-family: 'Work Sans', sans-serif;
  font-size: 14px;
  line-height: 1.55;
  color: var(--fg-muted);
  margin: 0 0 12px;
  text-wrap: pretty;
}

/* ── Meta row + source glyph ────────────────────────────────────────── */
.meta {
  display: flex;
  align-items: center;
  gap: 10px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  color: var(--fg-muted);
}
.meta .sep { color: var(--fg-subtle); }
.source-glyph {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  border-radius: 4px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 7.6px;
  font-weight: 600;
  letter-spacing: -0.02em;
  flex: 0 0 auto;
}

/* ── Archive page ───────────────────────────────────────────────────── */
.archive-head {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin: 40px 0 28px;
  gap: 16px;
  flex-wrap: wrap;
}
.archive-kicker {
  font-family: 'JetBrains Mono', monospace;
  font-size: 10.5px;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--accent);
  font-weight: 600;
}
.archive-head h2 {
  font-family: 'DM Serif Display', serif;
  font-weight: 400;
  font-size: clamp(36px, 5vw, 56px);
  line-height: 1.0;
  letter-spacing: -0.02em;
  color: var(--fg);
  margin: 10px 0 0;
}
.archive-meta {
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--fg-subtle);
}

.archive-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 16px;
}
.archive-card {
  padding: 22px;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--surface);
  transition: transform 0.2s ease, background 0.2s ease;
  display: block;
}
.archive-card:hover { transform: translateY(-2px); background: var(--surface-hi); border-color: var(--accent); }
.archive-card .edition {
  font-family: 'JetBrains Mono', monospace;
  font-size: 10.5px;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--accent);
  font-weight: 600;
  margin-bottom: 10px;
}
.archive-card .day {
  font-family: 'DM Serif Display', serif;
  font-weight: 400;
  font-size: 24px;
  line-height: 1.15;
  letter-spacing: -0.01em;
  color: var(--fg);
  margin: 0 0 14px;
}
.archive-card .count {
  font-family: 'JetBrains Mono', monospace;
  font-size: 10.5px;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: var(--fg-muted);
}

/* ── Footer ─────────────────────────────────────────────────────────── */
footer.endmark {
  padding: 48px 0;
  text-align: center;
}
footer.endmark .hairline {
  width: 32px;
  height: 1px;
  background: var(--fg-subtle);
  margin: 0 auto 14px;
}
footer.endmark .closing {
  font-family: 'JetBrains Mono', monospace;
  font-size: 10.5px;
  letter-spacing: 0.25em;
  text-transform: uppercase;
  color: var(--fg-subtle);
}

/* ── Responsive ─────────────────────────────────────────────────────── */
@media (max-width: 800px) {
  .shell { padding: 0 20px; }
  .section-grid.cols-2 { grid-template-columns: 1fr; gap: 28px; }
  .section-rule .bar { display: none; }
  .section-rule { flex-direction: column; gap: 12px; }
  .section-rule .links { justify-content: flex-start; }
}
"""


# ── Helpers ─────────────────────────────────────────────────────────────

def source_glyph_html(source: str) -> str:
    """Reproduces the React SourceGlyph: deterministic oklch hue + initials."""
    words = re.split(r"[\s']+", source.strip())
    words = [w for w in words if w]
    if not words:
        initials = "??"
    elif len(words) == 1:
        initials = words[0][:2].upper()
    else:
        initials = (words[0][0] + words[1][0]).upper()
    h = 0
    for c in source:
        h = (h * 31 + ord(c)) % 360
    bg = f"oklch(0.32 0.06 {h})"
    fg = f"oklch(0.88 0.08 {h})"
    return (
        f'<span class="source-glyph" style="background:{bg};color:{fg}">'
        f"{html.escape(initials)}</span>"
    )


def esc(s: str) -> str:
    return html.escape(s or "", quote=True)


def section_link(href: str, label: str, active_path: str) -> str:
    cls = "tab active" if href == active_path else "tab"
    return f'<a class="{cls}" href="{href}">{label}</a>'


def html_page(title: str, body_html: str, date_str: str = "",
              edition: str = "", section_names: list = None,
              article_count: str = "0", active_page: str = "today",
              fetched_at: str = "") -> str:
    """Render a full page with masthead + main + footer."""
    section_names = section_names or []
    if active_page == "today":
        sections_links = "".join(
            f'<a href="#sec-{esc(slugify(s))}">{esc(s)}</a>'
            for s in section_names
        )
    else:
        sections_links = "".join(
            f"<span>{esc(s)}</span>" for s in section_names
        )
    today_href = "index.html"
    archive_href = "archive.html"
    today_active = "tab active" if active_page == "today" else "tab"
    archive_active = "tab active" if active_page == "archive" else "tab"
    fetched_label = FETCH_TIME_LABEL
    if fetched_at:
        try:
            fetched_dt = datetime.fromisoformat(fetched_at)
            fetched_label = fetched_dt.strftime("%H:%M UTC")
        except Exception:
            pass
    stats_line = (
        f"{esc(article_count)} stories · fetched {fetched_label}"
        if active_page == "today" else "All editions"
    )
    edition_block = (
        f'<span>{esc(date_str)}</span>'
        f'<span class="sep">—</span>'
        f'<span>No. {esc(edition)}</span>'
    ) if active_page == "today" else (
        f'<span>The Archive</span>'
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}</title>
<style>{BASE_CSS}</style>
</head>
<body>
<div class="shell">
  <header class="masthead">
    <div class="eyebrow">A daily digest</div>
    <h1 class="title">Brief <span class="amp">&amp;</span> Co.</h1>
    <div class="dateline">{edition_block}</div>
    <div class="section-rule">
      <div class="bar"></div>
      <div class="links">{sections_links}</div>
      <div class="bar"></div>
    </div>
    <div class="subnav">
      <div class="tabs">
        <a class="{today_active}" href="{today_href}">Today</a>
        <a class="{archive_active}" href="{archive_href}">Archives</a>
      </div>
      <div class="stats">{stats_line}</div>
    </div>
  </header>
  <main>
{body_html}
  </main>
  <footer class="endmark">
    <div class="hairline"></div>
    <div class="closing">End of edition · see you at {FETCH_TIME_LABEL}</div>
  </footer>
</div>
</body>
</html>
"""


# ── Markdown parser (unchanged contract) ────────────────────────────────

def parse_markdown(md_path: Path):
    text = md_path.read_text(encoding="utf-8")

    meta = {}
    fm_match = re.match(r"^---\n(.+?)\n---\n", text, re.DOTALL)
    if fm_match:
        for line in fm_match.group(1).strip().split("\n"):
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
        text = text[fm_match.end():]

    sections = []
    current_section = None
    current_article = None

    for line in text.split("\n"):
        line_s = line.strip()
        if line_s.startswith("## "):
            if current_article and current_section:
                current_section["articles"].append(current_article)
            current_article = None
            current_section = {"title": line_s[3:], "articles": []}
            sections.append(current_section)
        elif line_s.startswith("### "):
            if current_article and current_section:
                current_section["articles"].append(current_article)
            link_match = re.match(r"\[(.+?)\]\((.+?)\)", line_s[4:])
            if link_match:
                current_article = {
                    "title": link_match.group(1),
                    "link": link_match.group(2),
                    "source": "",
                    "summary": "",
                }
            else:
                current_article = {
                    "title": line_s[4:],
                    "link": "",
                    "source": "",
                    "summary": "",
                }
        elif (
            current_article
            and not current_article["source"]
            and re.fullmatch(r"\*([^*]+)\*", line_s)
        ):
            current_article["source"] = line_s[1:-1]
        elif line_s == "---":
            pass
        elif line_s and current_article:
            if current_article["summary"]:
                current_article["summary"] += " " + line_s
            else:
                current_article["summary"] = line_s

    if current_article and current_section:
        current_section["articles"].append(current_article)

    return meta, sections


# ── Renderers ───────────────────────────────────────────────────────────

def render_meta(article) -> str:
    # Published time / read-time intentionally omitted — see chat handoff:
    # "Read-time removed from every story's meta row".
    return (
        '<div class="meta">'
        f'{source_glyph_html(article["source"])}'
        f'<span>{esc(article["source"])}</span>'
        '</div>'
    )


def render_hero(article, section_title: str) -> str:
    title_html = (
        f'<a href="{esc(article["link"])}" target="_blank" rel="noopener">'
        f'{esc(article["title"])}</a>'
        if article["link"] else esc(article["title"])
    )
    read_link = (
        f'<a class="read-link" href="{esc(article["link"])}" '
        f'target="_blank" rel="noopener">Read article →</a>'
        if article["link"] else ""
    )
    return f"""<article class="hero">
  <div class="hero-tag">Cover Story · {esc(section_title)}</div>
  <h2>{title_html}</h2>
  <p class="summary">{esc(article["summary"])}</p>
  <div class="hero-foot">
    {render_meta(article)}
    {read_link}
  </div>
</article>"""


def render_article(article) -> str:
    title_html = (
        f'<a href="{esc(article["link"])}" target="_blank" rel="noopener">'
        f'{esc(article["title"])}</a>'
        if article["link"] else esc(article["title"])
    )
    summary = (
        f'<p>{esc(article["summary"])}</p>' if article["summary"] else ""
    )
    return f"""<article class="article">
  <h4>{title_html}</h4>
  {summary}
  {render_meta(article)}
</article>"""


def render_section(section) -> str:
    articles = section["articles"]
    if not articles:
        return ""
    cols = "cols-2" if len(articles) > 1 else "cols-1"
    pieces = "piece" if len(articles) == 1 else "pieces"
    cards = "\n".join(render_article(a) for a in articles)
    anchor = slugify(section["title"])
    return f"""<section id="sec-{esc(anchor)}" class="section-block">
  <div class="section-head">
    <span class="glyph">§</span>
    <h3>{esc(section["title"])}</h3>
    <span class="count">{len(articles)} {pieces}</span>
  </div>
  <div class="section-grid {cols}">
{cards}
  </div>
</section>"""


def build_daily_page(md_path: Path, edition: str):
    meta, sections = parse_markdown(md_path)
    date_str = meta.get("date", "")
    title = meta.get("title", "Brief & Co.")

    try:
        article_count = int(meta.get("article_count", "0"))
    except ValueError:
        article_count = 0

    total_articles = sum(len(s["articles"]) for s in sections)
    if total_articles == 0:
        return None, date_str, 0

    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        formatted_date = format_long_date(dt)
    except Exception:
        formatted_date = date_str

    section_names = [s["title"] for s in sections if s["articles"]]

    lead_idx = next(
        (i for i, s in enumerate(sections) if s["articles"]), None
    )

    body_parts = []
    if lead_idx is not None:
        lead_section = sections[lead_idx]
        body_parts.append(render_hero(lead_section["articles"][0], lead_section["title"]))

    for i, section in enumerate(sections):
        articles = section["articles"][1:] if i == lead_idx else section["articles"]
        if not articles:
            continue
        body_parts.append(render_section({"title": section["title"], "articles": articles}))

    body = "\n".join(body_parts)
    page = html_page(
        title=title,
        body_html=body,
        date_str=formatted_date,
        edition=edition,
        section_names=section_names,
        article_count=str(article_count or total_articles),
        active_page="today",
        fetched_at=meta.get("fetched_at", ""),
    )
    return page, date_str, article_count or total_articles


def build_archive_page(all_dates):
    """List all editions as a card grid."""
    sorted_dates = sorted(all_dates, key=lambda x: x[0], reverse=True)
    cards = []
    for date_str, count, edition in sorted_dates:
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            day_label = format_long_date(dt)
        except Exception:
            day_label = date_str
        pieces = "story" if int(count) == 1 else "stories"
        cards.append(f"""<a class="archive-card" href="{esc(date_str)}.html">
  <div class="edition">No. {esc(edition)}</div>
  <div class="day">{esc(day_label)}</div>
  <div class="count">{count} {pieces}</div>
</a>""")

    body = f"""<div class="archive-head">
  <div>
    <div class="archive-kicker">Archives</div>
    <h2>Past editions</h2>
  </div>
  <div class="archive-meta">{len(sorted_dates)} editions</div>
</div>
<div class="archive-grid">
{''.join(cards)}
</div>"""

    return html_page(
        title="Archives — Brief & Co.",
        body_html=body,
        active_page="archive",
    )


def build_site():
    print("=" * 60)
    print("  Daily News Bulletin — Site Builder (Brief & Co.)")
    print("=" * 60)

    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    daily_dirs = sorted(CONTENT_DIR.glob("*/index.md"))
    if not daily_dirs:
        print("\nNo content found in content/. Run fetch_news.py first.")
        return

    editions = assign_editions([md.parent.name for md in daily_dirs])

    all_dates = []
    pages = {}
    today_str = datetime.now().strftime("%Y-%m-%d")

    for md_path in daily_dirs:
        date_dir = md_path.parent.name
        edition = str(editions[date_dir])
        page_html, date_str, count = build_daily_page(md_path, edition)

        if page_html is None:
            print(f"  Skipped: {date_dir} (no articles)")
            continue

        out_path = DOCS_DIR / f"{date_dir}.html"
        out_path.write_text(page_html, encoding="utf-8")
        print(f"  Built: {out_path.name}")

        all_dates.append((date_str, count, edition))
        pages[date_str] = page_html

    if not pages:
        print("\nAll content was empty. Nothing to build.")
        return

    valid_dates = sorted([d for d in pages if d <= today_str], reverse=True)
    latest_date = valid_dates[0] if valid_dates else sorted(pages.keys(), reverse=True)[0]
    (DOCS_DIR / "index.html").write_text(pages[latest_date], encoding="utf-8")
    print(f"  Built: index.html ({latest_date})")

    archive_html = build_archive_page(all_dates)
    (DOCS_DIR / "archive.html").write_text(archive_html, encoding="utf-8")
    print(f"  Built: archive.html ({len(all_dates)} days)")

    print(f"\nSite ready at: {DOCS_DIR}/index.html")


if __name__ == "__main__":
    build_site()
