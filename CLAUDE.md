# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A static-site daily news bulletin. RSS feeds → markdown → HTML, published from `docs/` (GitHub Pages layout). No framework, no build tool, no package manager — three plain Python scripts.

## Common commands

```bash
python3 run.py            # full pipeline: fetch then build
python3 fetch_news.py     # just refresh content/<date>/index.md from RSS
python3 build_site.py     # just regenerate docs/ from existing markdown
```

The only runtime dep is `feedparser`, which `fetch_news.py` self-installs via `pip --break-system-packages` if missing. There is no `requirements.txt`, no test suite, no linter config.

To preview locally: `python3 -m http.server 8000 -d docs` then open `http://localhost:8000`.

## Architecture

Two-stage pipeline with the filesystem as the only state:

1. **`fetch_news.py`** reads `feeds.json`, pulls each RSS feed (capped at 15 entries each, articles older than `MAX_ARTICLE_AGE_DAYS = 7` skipped, future-dated entries beyond 24h skipped), groups articles by published date, and writes `content/<YYYY-MM-DD>/index.md`. Each markdown file has YAML-ish frontmatter (`date`, `title`, `article_count`) followed by `## Category` / `### [Title](url)` / `*Source*` / summary blocks. Categories are emitted in the fixed `CATEGORY_ORDER` list at the top of `fetch_news.py` — adding a new category to `feeds.json` without updating `CATEGORY_ORDER` will sort it to the end (rank 99).

2. **`build_site.py`** parses every `content/*/index.md` with a hand-rolled regex parser (no markdown library), renders one HTML page per day plus `archive.html`, and copies the most-recent date `<= today` to `index.html`. All CSS is the `BASE_CSS` string constant inside `build_site.py` — there is no separate stylesheet, and the `templates/` directory is a stale output dump, NOT a Jinja-style template source. To restyle the site, edit `BASE_CSS` directly.

`docs/` is the GitHub Pages publish root. `content/` is committed source-of-truth markdown. Re-running `fetch_news.py` overwrites the day's `index.md` rather than merging — running it twice on the same day replaces, not appends.

`feeds.json` is the only config: a flat array of `{name, feed_url, website, category}`. Adding a feed there is the entire "add a source" workflow.

## Conventions worth knowing

- Article dedup is by `md5(title + link)[:10]` but is *not* enforced across runs — re-running the fetcher on a day rebuilds from feed state, so duplicates only matter within a single fetch.
- The "lead story" on each daily page is just the first article of the first non-empty section after `CATEGORY_ORDER` sorting. To change which story leads, reorder `CATEGORY_ORDER` or edit the markdown by hand before rebuilding.
- Layout is responsive but column counts are hardcoded in `build_site.py` (`>=3` → 3-col grid, `==2` → 2-col, `1` → single). If you need a different layout per section, change `build_daily_page`.

## Date handling note

The repo treats `datetime.now()` as authoritative; there is no fixed publish date. The user's environment reports today as 2026-05-06, and `content/` already has dated dirs in 2026 — this is normal, not a clock issue.

## graphify

This project has a graphify knowledge graph at graphify-out/.

Rules:
- Before answering architecture or codebase questions, read graphify-out/GRAPH_REPORT.md for god nodes and community structure
- If graphify-out/wiki/index.md exists, navigate it instead of reading raw files
- After modifying code files in this session, run `python3 -c "from graphify.watch import _rebuild_code; from pathlib import Path; _rebuild_code(Path('.'))"` to keep the graph current
