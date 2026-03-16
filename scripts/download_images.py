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


# ⚡ Maps data.json display names to their correct wiki image slug where the
# default name-to-slug conversion would produce a 404.  Multiple data.json
# entries can share the same display name (e.g. one per build-piece material),
# so they all resolve to the same dest path and the file is only downloaded once.
WIKI_NAME_OVERRIDES = {
    # Renamed machines
    "Coal Generator": "Coal-Powered_Generator",
    "Fuel Generator": "Fuel-Powered_Generator",
    "Blueprint Designer": "Blueprint_Designer_Mk.1",
    # Foundations
    "Foundation 1m": "Foundation_1m_(FICSIT)",
    "Foundation 2m": "Foundation_1m_(FICSIT)",
    "Foundation 4m": "Foundation_4m_(FICSIT)",
    "Half 1m Foundation": "Half_Foundation_1m_(FICSIT)",
    "Half 2m Foundation": "Half_Foundation_1m_(FICSIT)",
    "Half 4m Foundation": "Half_Foundation_4m_(FICSIT)",
    # Ramps
    "Ramp 1m": "Ramp_1m_(FICSIT)",
    "Ramp 2m": "Ramp_1m_(FICSIT)",
    "Ramp 4m": "Ramp_4m_(FICSIT)",
    "Up Corner Ramp 1m": "Up_Corner_Ramp_4m_(FICSIT)",
    "Up Corner Ramp 2m": "Up_Corner_Ramp_4m_(FICSIT)",
    "Up Corner Ramp 4m": "Up_Corner_Ramp_4m_(FICSIT)",
    "Down Corner Ramp 1m": "Down_Corner_Ramp_4m_(FICSIT)",
    "Down Corner Ramp 2m": "Down_Corner_Ramp_4m_(FICSIT)",
    "Down Corner Ramp 4m": "Down_Corner_Ramp_4m_(FICSIT)",
    "Double Ramp 2m": "Double_Ramp_8m_(FICSIT)",
    "Double Ramp 4m": "Double_Ramp_8m_(FICSIT)",
    "Double Ramp 8m": "Double_Ramp_8m_(FICSIT)",
    "Inv. Ramp 1m": "Inv._Ramp_4m_(FICSIT)",
    "Inv. Ramp 2m": "Inv._Ramp_4m_(FICSIT)",
    "Inv. Ramp 4m": "Inv._Ramp_4m_(FICSIT)",
    "Inv. Up Corner 1m": "Inv._Up_Corner_4m_(FICSIT)",
    "Inv. Up Corner 2m": "Inv._Up_Corner_4m_(FICSIT)",
    "Inv. Up Corner 4m": "Inv._Up_Corner_4m_(FICSIT)",
    "Inv. Down Corner 1m": "Inv._Down_Corner_4m_(FICSIT)",
    "Inv. Down Corner 2m": "Inv._Down_Corner_4m_(FICSIT)",
    "Inv. Down Corner 4m": "Inv._Down_Corner_4m_(FICSIT)",
    # Quarter pipes
    "Quarter Pipe": "Quarter_Pipe_(FICSIT)",
    "Inverted Quarter Pipe": "Inverted_Quarter_Pipe_(FICSIT)",
    "Inner Corner Quarter Pipe": "Inner_Corner_Quarter_Pipe_(FICSIT)",
    "Inverted Inner Corner Quarter Pipe": "Inverted_Inner_Corner_Quarter_Pipe_(FICSIT)",
    "Outer Corner Quarter Pipe": "Outer_Corner_Quarter_Pipe_(FICSIT)",
    "Inverted Outer Corner Quarter Pipe": "Inverted_Outer_Corner_Quarter_Pipe_(FICSIT)",
    "Inner Corner Extension 1m": "Inner_Corner_Extension_4m_(FICSIT)",
    "Inner Corner Extension 2m": "Inner_Corner_Extension_4m_(FICSIT)",
    "Inner Corner Extension 4m": "Inner_Corner_Extension_4m_(FICSIT)",
    "Outer Corner Extension 1m": "Outer_Corner_Extension_4m_(FICSIT)",
    "Outer Corner Extension 2m": "Outer_Corner_Extension_4m_(FICSIT)",
    "Outer Corner Extension 4m": "Outer_Corner_Extension_4m_(FICSIT)",
    # Ramp walls
    "Ramp Wall 1m": "Ramp_Wall_1m_(FICSIT)",
    "Ramp Wall 2m": "Ramp_Wall_2m_(FICSIT)",
    "Ramp Wall 4m": "Ramp_Wall_4m_(FICSIT)",
    "Ramp Wall 8m": "Ramp_Wall_8m_(FICSIT)",
    "Inv. Ramp Wall 1m": "Inv._Ramp_Wall_1m_(FICSIT)",
    "Inv. Ramp Wall 2m": "Inv._Ramp_Wall_2m_(FICSIT)",
    "Inv. Ramp Wall 4m": "Inv._Ramp_Wall_4m_(FICSIT)",
    "Inv. Ramp Wall 8m": "Inv._Ramp_Wall_8m_(FICSIT)",
    # Walls
    "Basic Wall 1m": "Basic_Wall_1m_(FICSIT)",
    "Basic Wall 4m": "Basic_Wall_4m_(FICSIT)",
    "Center Door Wall": "Center_Door_Wall_(FICSIT)",
    "Side Door Wall": "Side_Door_Wall_(FICSIT)",
    "Gate Hole Wall": "Gate_Hole_Wall_(FICSIT)",
    "Conveyor Wall x1": "Conveyor_Wall_x1_(FICSIT)",
    "Conveyor Wall x2": "Conveyor_Wall_x2_(FICSIT)",
    "Conveyor Wall x3": "Conveyor_Wall_x3_(FICSIT)",
    # Windows
    "Frame Window": "Frame_Window_(FICSIT)",
    "Panel Window": "Panel_Window_(FICSIT)",
    "Single Window": "Single_Window_(FICSIT)",
    "Reinforced Window": "Reinforced_Window_(FICSIT)",
    # Roofs
    "Roof 1m": "FICSIT_Roof_1m",
    "Roof 2m": "FICSIT_Roof_2m",
    "Roof 4m": "FICSIT_Roof_4m",
    "Roof Flat": "FICSIT_Roof_Flat",
    "Inner Corner Roof 1m": "Inner_Corner_Roof_1m_(FICSIT)",
    "Inner Corner Roof 2m": "Inner_Corner_Roof_2m_(FICSIT)",
    "Inner Corner Roof 4m": "Inner_Corner_Roof_4m_(FICSIT)",
    "Outer Corner Roof 1m": "Outer_Corner_Roof_1m_(FICSIT)",
    "Outer Corner Roof 2m": "Outer_Corner_Roof_2m_(FICSIT)",
    "Outer Corner Roof 4m": "Outer_Corner_Roof_4m_(FICSIT)",
    # Pipeline
    "Pipeline Junction Cross": "Pipeline_Junction",
}


def wiki_url(wiki_slug: str, size: int) -> str:
    """Return the wiki.gg thumbnail URL for a given wiki image slug."""
    encoded_slug = urllib.parse.quote(wiki_slug, safe="_")
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

        # ⚡ Use override wiki slug if available, otherwise derive from name
        wiki_slug = WIKI_NAME_OVERRIDES.get(name) or name.replace(" ", "_")
        url = wiki_url(wiki_slug, size)
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
