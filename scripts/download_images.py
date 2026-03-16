"""Download all item images from satisfactory.wiki.gg to app/static/images/.

Usage:
    python scripts/download_images.py          # download both 64px and 256px
    python scripts/download_images.py 256      # download only 256px

Idempotent -- skips files that already exist. Run once after cloning the repo.
Images are committed to the repo (~2MB) for stlite/GitHub Pages compatibility.

Directory structure:
    app/static/images/64/{slug}.png   -- thumbnails (chips, grid icons)
    app/static/images/256/{slug}.png  -- hero cards (objective cards, detail views)
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
IMAGES_BASE = REPO_ROOT / "app" / "static" / "images"

SIZES = [64, 256]  # px — small for chips, large for hero cards


def image_slug(name: str) -> str:
    """Convert item display name to a filesystem-safe slug."""
    return name.replace(" ", "_").replace("'", "_").replace(":", "_")


def wiki_url(name: str, size: int) -> str:
    """Return the wiki.gg thumbnail URL for an item."""
    slug = name.replace(" ", "_")
    # URL-encode non-ASCII characters (e.g. trademark symbol)
    encoded_slug = urllib.parse.quote(slug, safe="_")
    return f"https://satisfactory.wiki.gg/images/thumb/{encoded_slug}.png/{size}px-{encoded_slug}.png"


def download_size(items: dict, size: int):
    """Download all items at a given size."""
    dest_dir = IMAGES_BASE / str(size)
    dest_dir.mkdir(parents=True, exist_ok=True)

    total = len(items)
    downloaded = 0
    skipped = 0
    failed = []

    print(f">> Downloading {total} item images at {size}px to {dest_dir}")
    print()

    for i, (key, item) in enumerate(sorted(items.items(), key=lambda x: x[1].get("name", "")), 1):
        name = item.get("name", key)
        slug = image_slug(name)
        dest = dest_dir / f"{slug}.png"

        if dest.exists():
            skipped += 1
            print(f"  [{i:3d}/{total}] {name} ... skipped (exists)")
            continue

        url = wiki_url(name, size)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "ULTRA-SATISFACTORY/1.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                dest.write_bytes(resp.read())
            downloaded += 1
            print(f"  [{i:3d}/{total}] {name} ... ok")
            # Be polite to wiki.gg
            time.sleep(0.1)
        except (urllib.error.URLError, urllib.error.HTTPError, OSError) as e:
            failed.append((name, str(e)))
            print(f"  [{i:3d}/{total}] {name} ... FAILED ({e})")

    print()
    print(f">> {size}px done: {downloaded} downloaded, {skipped} skipped, {len(failed)} failed")
    if failed:
        print(f"   Failed items:")
        for name, err in failed:
            print(f"     - {name}: {err}")
    return failed


def main():
    with open(DATA_PATH, encoding="utf-8") as f:
        data = json.load(f)

    # Collect all unique item names (items minus raw resources)
    resource_keys = set(data.get("resources", {}).keys())
    items = {
        key: item
        for key, item in data.get("items", {}).items()
        if key not in resource_keys
    }

    # Allow filtering to a single size via CLI arg
    sizes = SIZES
    if len(sys.argv) > 1:
        sizes = [int(sys.argv[1])]

    all_failed = []
    for size in sizes:
        failed = download_size(items, size)
        all_failed.extend(failed)

    if all_failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
