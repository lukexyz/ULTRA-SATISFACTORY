"""⚡ Download all item images from satisfactory.wiki.gg to app/static/images/.

Usage:
    python scripts/download_images.py

Idempotent — skips files that already exist. Run once after cloning the repo.
Images are committed to the repo (~2MB) for stlite/GitHub Pages compatibility.
"""

import json
import sys
import time
import urllib.request
import urllib.error
import urllib.parse
from pathlib import Path

# Resolve paths relative to this script
REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = REPO_ROOT / "data" / "data.json"
IMAGES_DIR = REPO_ROOT / "app" / "static" / "images"
IMAGE_SIZE = 64  # px — small enough for grid/chip icons, big enough for clarity


def image_slug(name: str) -> str:
    """Convert item display name to a filesystem-safe slug."""
    return name.replace(" ", "_").replace("'", "_").replace(":", "_")


def wiki_url(name: str, size: int = IMAGE_SIZE) -> str:
    """Return the wiki.gg thumbnail URL for an item."""
    slug = name.replace(" ", "_")
    # URL-encode non-ASCII characters (e.g. trademark symbol)
    encoded_slug = urllib.parse.quote(slug, safe="_")
    return f"https://satisfactory.wiki.gg/images/thumb/{encoded_slug}.png/{size}px-{encoded_slug}.png"


def download_all():
    with open(DATA_PATH, encoding="utf-8") as f:
        data = json.load(f)

    # Collect all unique item names (items minus raw resources)
    resource_keys = set(data.get("resources", {}).keys())
    items = {
        key: item
        for key, item in data.get("items", {}).items()
        if key not in resource_keys
    }

    IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    total = len(items)
    downloaded = 0
    skipped = 0
    failed = []

    print(f">> Downloading {total} item images to {IMAGES_DIR}")
    print(f"   Source: satisfactory.wiki.gg ({IMAGE_SIZE}px thumbnails)")
    print()

    for i, (key, item) in enumerate(sorted(items.items(), key=lambda x: x[1].get("name", "")), 1):
        name = item.get("name", key)
        slug = image_slug(name)
        dest = IMAGES_DIR / f"{slug}.png"

        if dest.exists():
            skipped += 1
            print(f"  [{i:3d}/{total}] {name} ... skipped (exists)")
            continue

        url = wiki_url(name)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "ULTRA-SATISFACTORY/1.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                dest.write_bytes(resp.read())
            downloaded += 1
            print(f"  [{i:3d}/{total}] {name} ... ok")
            # Be polite to wiki.gg — small delay between requests
            time.sleep(0.1)
        except (urllib.error.URLError, urllib.error.HTTPError, OSError) as e:
            failed.append((name, str(e)))
            print(f"  [{i:3d}/{total}] {name} ... FAILED ({e})")

    print()
    print(f">> Done: {downloaded} downloaded, {skipped} skipped, {len(failed)} failed")
    if failed:
        print(f"  Failed items:")
        for name, err in failed:
            print(f"    - {name}: {err}")
        sys.exit(1)


if __name__ == "__main__":
    download_all()
