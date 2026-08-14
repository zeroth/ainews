---
date: 2026-08-13
title: Daily Bulletin — Thursday, August 13, 2026
article_count: 9
fetched_at: 2026-08-14T21:20:41+00:00
---

## AI Tools & Models

### [alchemy-utils 0.1a1](https://simonwillison.net/2026/Aug/13/alchemy-utils)
*Simon Willison's Weblog*

Release: alchemy-utils 0.1a1 Performance boost for DuckDB exports and CSV imports, see here.

---

### [llm-gemini 0.33](https://simonwillison.net/2026/Aug/13/llm-gemini)
*Simon Willison's Weblog*

Release: llm-gemini 0.33 It's been a while since the last llm-gemini release. This version of the plugin adds support for today's Gemini 3.7 Flash release, plus gemini-3.6-flash, gemini-3.5-flash-lite and two embedding models gemini-embedding-2 and gemini-embedding-001. The plugin is also upgraded...

---

### [sqlite-utils 4.2](https://simonwillison.net/2026/Aug/13/sqlite-utils)
*Simon Willison's Weblog*

Release: sqlite-utils 4.2 Lots of improvements in this one relating to the table.transform() feature, which adds support for complex alter table operations by creating a fresh table, copying across the data and then dropping and replacing the old one. transform() now preserves a much larger array...

---

### [sqlite-utils 4.2.1](https://simonwillison.net/2026/Aug/13/sqlite-utils-2)
*Simon Willison's Weblog*

Release: sqlite-utils 4.2.1 Fixes a crashing bug in sqlite-utils 4.2. I'd introduced code that looks like this: from typing_extensions import Self It turned out the typing-extensions package was not listed as a dependency for sqlite-utils - it was installed by one of the other dependencies in the...

---

## Enterprise AI & Vision

### [Team Stories about ADE Gen2: Engineers on Camera](https://landing.ai/blog/agentic-document-extraction-second-generation-team-stories)
*Landing AI Blog*

Eight LandingAI builders on Agentic Document Extraction Second Generation: document grounding, atomic citations, and the launch moment that went silent. Watch the clips.

---

### [Build Faster with ADE Claude Skills](https://landing.ai/blog/build-faster-with-ade-claude-skill)
*Landing AI Blog*

The ADE Claude Skill teaches Claude Code how LandingAI's Agentic Document Extraction actually works — Parse, Build Schema, and Extract — so the pipelines it writes follow best practices. Install it in three commands, then start from a prompt library covering quickstart, batch-to-CSV, invoice...

---

### [How to Configure Parse Output](https://landing.ai/blog/how-to-configure-parse-output)
*Landing AI Blog*

A single options object controls the shape of every DPT-3 Parse response. This guide walks through each knob — pages, table format, per-block markdown, atomic_grounding, and inline_markdown — with its default, so you can start from defaults and turn one at a time.

---

### [The ADE Vocabulary: Six Core Concepts](https://landing.ai/blog/the-ade-vocabulary-six-core-concepts)
*Landing AI Blog*

Agentic Document Extraction is built from six composable operations — Parse, Extract, Classify, Split, Section, and Grounding. Learn what each one does, when to reach for it, and how they stack into a working document pipeline.

---

### [Understanding Parse Output: Markdown, Structure, and Metadata](https://landing.ai/blog/understanding-parse-output)
*Landing AI Blog*

A DPT-3 parse returns three top-level fields — markdown to read the document, structure to locate every block, and metadata to account for the job. Grounding rides inline on each block, so every value traces back to the exact line and box it came from.

---
