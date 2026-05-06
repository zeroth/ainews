#!/usr/bin/env python3
"""
Daily News Bulletin — One-command pipeline
Fetches RSS feeds and builds the static site.
Usage: python3 run.py
"""

import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()

def main():
    print("\n🗞️  Daily News Bulletin\n")

    # Step 1: Fetch
    print("Step 1/2: Fetching news...\n")
    result = subprocess.run(
        [sys.executable, str(SCRIPT_DIR / "fetch_news.py")],
        cwd=str(SCRIPT_DIR),
    )
    if result.returncode != 0:
        print("Fetch failed!")
        sys.exit(1)

    # Step 2: Build
    print("\nStep 2/2: Building site...\n")
    result = subprocess.run(
        [sys.executable, str(SCRIPT_DIR / "build_site.py")],
        cwd=str(SCRIPT_DIR),
    )
    if result.returncode != 0:
        print("Build failed!")
        sys.exit(1)

    index = SCRIPT_DIR / "docs" / "index.html"
    print(f"\n✅ Done! Open: {index}")


if __name__ == "__main__":
    main()
