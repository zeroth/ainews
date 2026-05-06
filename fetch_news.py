#!/usr/bin/env python3
"""
Daily News Bulletin - RSS Fetcher
Fetches articles from configured RSS feeds and saves them as markdown files
organized by date in the content/ directory.
"""

import json
import os
import sys
import hashlib
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode

try:
    import feedparser
except ImportError:
    print("Installing feedparser...")
    os.system(f"{sys.executable} -m pip install feedparser --break-system-packages -q")
    import feedparser

# ── Config ──────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).parent.resolve()
FEEDS_FILE = SCRIPT_DIR / "feeds.json"
CONTENT_DIR = SCRIPT_DIR / "content"
SEEN_FILE = SCRIPT_DIR / "seen.json"
MAX_ARTICLE_AGE_DAYS = 3  # fetch articles from last N days

# Tracking params dropped during link normalization (so the same article shared
# from multiple sources dedupes to one ID).
TRACKING_PARAMS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "fbclid", "gclid", "mc_cid", "mc_eid", "ref", "ref_src",
    "_hsenc", "_hsmi", "_branch_match_id", "igshid",
}


def normalize_link(url: str) -> str:
    """Drop tracking params, lowercase host, strip trailing slash."""
    if not url:
        return ""
    try:
        p = urlparse(url)
        q = [
            (k, v) for k, v in parse_qsl(p.query, keep_blank_values=True)
            if k.lower() not in TRACKING_PARAMS
        ]
        path = p.path.rstrip("/") or "/"
        return urlunparse((
            p.scheme.lower(), p.netloc.lower(), path, p.params, urlencode(q), ""
        ))
    except Exception:
        return url


def load_seen() -> dict:
    if SEEN_FILE.exists():
        try:
            return json.loads(SEEN_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_seen(seen: dict) -> None:
    SEEN_FILE.write_text(
        json.dumps(seen, indent=2, sort_keys=True), encoding="utf-8"
    )

# Category display order (security first, then by relevance)
CATEGORY_ORDER = [
    "Security",
    "AI Security",
    "AI Labs",
    "AI Policy & Safety",
    "AI Tools & Models",
    "AI Agents",
    "AI Coding Tools",
    "Prompt & Context Engineering",
    "ML & Model Development",
    "AI Product & UX",
    "AI Infrastructure",
    "Open Source AI",
    "Building AI Agents & Architecture",
    "Data Engineering for AI",
    "Enterprise AI & MLOps",
    "Software Architecture",
]


def load_feeds():
    with open(FEEDS_FILE) as f:
        return json.load(f)


def parse_date(entry):
    """Extract and normalize published date from a feed entry."""
    for attr in ("published_parsed", "updated_parsed"):
        parsed = getattr(entry, attr, None)
        if parsed:
            try:
                from time import mktime

                return datetime.fromtimestamp(mktime(parsed), tz=timezone.utc)
            except Exception:
                pass
    # fallback: try dateutil
    for attr in ("published", "updated"):
        raw = getattr(entry, attr, None)
        if raw:
            try:
                from email.utils import parsedate_to_datetime

                return parsedate_to_datetime(raw).astimezone(timezone.utc)
            except Exception:
                pass
    return None


def clean_html(text):
    """Strip HTML tags from text for summary."""
    import re

    text = re.sub(r"<[^>]+>", "", text or "")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def get_summary(entry, max_len=300):
    """Get a clean summary from the entry."""
    raw = ""
    if hasattr(entry, "summary"):
        raw = entry.summary
    elif hasattr(entry, "description"):
        raw = entry.description
    elif hasattr(entry, "content") and entry.content:
        raw = entry.content[0].get("value", "")
    text = clean_html(raw)
    if len(text) > max_len:
        text = text[:max_len].rsplit(" ", 1)[0] + "..."
    return text


def fetch_all(feeds, cutoff, seen, today_str):
    """Fetch articles from all feeds.

    Cross-day dedup: an article is skipped if its id is already in `seen`
    AND was first seen on a different date. Same-day re-runs keep their
    articles so re-running today doesn't shrink today's bulletin.
    `seen` is mutated in place — caller writes it back to disk.
    """
    articles = []
    skipped_dedup = 0
    for feed_info in feeds:
        name = feed_info["name"]
        url = feed_info["feed_url"]
        category = feed_info["category"]
        print(f"  Fetching: {name}...", end=" ", flush=True)
        try:
            parsed = feedparser.parse(url)
            count = 0
            for entry in parsed.entries[:15]:  # limit per feed
                pub_date = parse_date(entry)
                if pub_date and pub_date < cutoff:
                    continue
                if pub_date is None:
                    pub_date = datetime.now(timezone.utc)
                # Skip articles with future dates (e.g. event listings)
                if pub_date > datetime.now(timezone.utc) + timedelta(hours=24):
                    continue
                title = getattr(entry, "title", "Untitled")
                raw_link = getattr(entry, "link", "")
                link = normalize_link(raw_link)
                article_id = hashlib.md5(f"{title}{link}".encode()).hexdigest()[:10]

                prior = seen.get(article_id)
                if prior and prior.get("first_seen") != today_str:
                    skipped_dedup += 1
                    continue

                summary = get_summary(entry)
                articles.append(
                    {
                        "id": article_id,
                        "title": title,
                        "link": link,
                        "summary": summary,
                        "source": name,
                        "source_url": feed_info["website"],
                        "category": category,
                        "date": pub_date.strftime("%Y-%m-%d"),
                        "datetime": pub_date.isoformat(),
                    }
                )
                seen[article_id] = {
                    "first_seen": prior["first_seen"] if prior else today_str,
                    "link": link,
                    "title": title,
                }
                count += 1
            print(f"{count} articles")
        except Exception as e:
            print(f"ERROR: {e}")
    if skipped_dedup:
        print(f"\nDeduped {skipped_dedup} previously-seen articles")
    return articles


def save_daily_markdown(articles):
    """Group articles by date and save as markdown files."""
    by_date = {}
    for a in articles:
        by_date.setdefault(a["date"], []).append(a)

    for date_str, day_articles in by_date.items():
        date_dir = CONTENT_DIR / date_str
        date_dir.mkdir(parents=True, exist_ok=True)

        # Sort by category order
        cat_rank = {c: i for i, c in enumerate(CATEGORY_ORDER)}
        day_articles.sort(
            key=lambda a: (cat_rank.get(a["category"], 99), a["datetime"])
        )

        md_path = date_dir / "index.md"
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        lines = [
            f"---",
            f"date: {date_str}",
            f"title: Daily Bulletin — {dt.strftime('%A, %B %-d, %Y')}",
            f"article_count: {len(day_articles)}",
            f"---",
            f"",
        ]

        current_cat = None
        for a in day_articles:
            if a["category"] != current_cat:
                current_cat = a["category"]
                lines.append(f"## {current_cat}")
                lines.append("")

            lines.append(f"### [{a['title']}]({a['link']})")
            lines.append(f"*{a['source']}*")
            lines.append("")
            if a["summary"]:
                lines.append(a["summary"])
                lines.append("")
            lines.append("---")
            lines.append("")

        md_path.write_text("\n".join(lines), encoding="utf-8")
        print(f"  Saved: {md_path} ({len(day_articles)} articles)")


def main():
    print("=" * 60)
    print("  Daily News Bulletin — RSS Fetcher")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    feeds = load_feeds()
    print(f"\nLoaded {len(feeds)} feeds from {FEEDS_FILE.name}")

    cutoff = datetime.now(timezone.utc) - timedelta(days=MAX_ARTICLE_AGE_DAYS)
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    seen = load_seen()
    print(f"Fetching articles since {cutoff.strftime('%Y-%m-%d')}...")
    print(f"Seen index: {len(seen)} articles tracked\n")

    articles = fetch_all(feeds, cutoff, seen, today_str)
    print(f"\nTotal articles fetched: {len(articles)}")

    save_seen(seen)

    if articles:
        save_daily_markdown(articles)
    else:
        print("No new articles.")

    return articles


if __name__ == "__main__":
    main()
