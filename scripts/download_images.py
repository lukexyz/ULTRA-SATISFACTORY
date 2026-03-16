"""Download item and/or building images from satisfactory.wiki.gg to app/static/images/.

Usage:
    python scripts/download_images.py                  # download items + buildings, 64px + 512px
    python scripts/download_images.py --items          # items only
    python scripts/download_images.py --buildings      # buildings only
    python scripts/download_images.py --size 64        # override size(s), comma-separated
    python scripts/download_images.py --buildings --size 64,512

Idempotent -- skips files that already exist.
Images are committed to the repo for stlite/GitHub Pages compatibility.

Directory structure:
    app/static/images/64/{slug}.png    -- thumbnails (chips, grid icons)
    app/static/images/512/{slug}.png   -- hero cards (detail views, objective cards)
"""

import argparse
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

# Resolve paths relative to this script
REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = REPO_ROOT / "data" / "data.json"
IMAGES_BASE = REPO_ROOT / "app" / "static" / "images"

DEFAULT_SIZES = [64, 512]


def image_slug(name: str) -> str:
    """Convert display name to a filesystem-safe slug. Must match data.py exactly."""
    return name.replace(" ", "_").replace("'", "_").replace(":", "_")


def wiki_url(name: str, size: int) -> str:
    """Return the wiki.gg thumbnail URL for an item or building."""
    slug = name.replace(" ", "_")
    encoded_slug = urllib.parse.quote(slug, safe="_")
    return f"https://satisfactory.wiki.gg/images/thumb/{encoded_slug}.png/{size}px-{encoded_slug}.png"


def download_size(entries: dict, size: int, label: str = "entries"):
    """Download all entries at a given size.

    entries: dict of {class_key: {"name": display_name, ...}}
    """
    dest_dir = IMAGES_BASE / str(size)
    dest_dir.mkdir(parents=True, exist_ok=True)

    total = len(entries)
    downloaded = 0
    skipped = 0
    failed = []

    print(f"\n>> Downloading {total} {label} images at {size}px to {dest_dir}")

    for i, (key, item) in enumerate(sorted(entries.items(), key=lambda x: x[1].get("name", "")), 1):
        name = item.get("name", key)
        slug = image_slug(name)
        dest = dest_dir / f"{slug}.png"

        if dest.exists():
            skipped += 1
            print(f"  [{i:3d}/{total}] {name} ... skipped")
            continue

        url = wiki_url(name, size)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "ULTRA-SATISFACTORY/1.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                dest.write_bytes(resp.read())
            downloaded += 1
            print(f"  [{i:3d}/{total}] {name} ... ok")
            time.sleep(0.1)  # be polite to wiki.gg
        except (urllib.error.URLError, urllib.error.HTTPError, OSError) as e:
            failed.append((name, str(e)))
            print(f"  [{i:3d}/{total}] {name} ... FAILED ({e})")

    print(f"\n>> {size}px {label}: {downloaded} downloaded, {skipped} skipped, {len(failed)} failed")
    if failed:
        print("   Failed entries:")
        for name, err in failed:
            print(f"     - {name}: {err}")
    return failed


def main():
    parser = argparse.ArgumentParser(description="Download Satisfactory wiki images.")
    parser.add_argument("--items", action="store_true", help="Download item images only")
    parser.add_argument("--buildings", action="store_true", help="Download building images only")
    parser.add_argument(
        "--size",
        type=str,
        default=None,
        help="Comma-separated sizes in px (default: 64,512)",
    )
    args = parser.parse_args()

    # If neither flag given, download both
    do_items = args.items or (not args.items and not args.buildings)
    do_buildings = args.buildings or (not args.items and not args.buildings)

    sizes = DEFAULT_SIZES
    if args.size:
        sizes = [int(s.strip()) for s in args.size.split(",")]

    with open(DATA_PATH, encoding="utf-8") as f:
        data = json.load(f)

    all_failed = []

    if do_items:
        resource_keys = set(data.get("resources", {}).keys())
        items = {
            key: item
            for key, item in data.get("items", {}).items()
            if key not in resource_keys
        }
        for size in sizes:
            failed = download_size(items, size, label="item")
            all_failed.extend(failed)

    if do_buildings:
        buildings = data.get("buildings", {})
        for size in sizes:
            failed = download_size(buildings, size, label="building")
            all_failed.extend(failed)

    print(f"\n>> Total failed: {len(all_failed)}")
    if all_failed:
        import sys
        sys.exit(1)


if __name__ == "__main__":
    main()
