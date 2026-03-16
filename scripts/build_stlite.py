"""
⚡ Build script for stlite deployment.

Reads app/app.py and ultra_satisfactory/data.py, adapts them for the stlite
runtime (Pyodide/WebAssembly), and generates docs/index.html with the stlite
mount() call. Copies data/data.json and images into docs/.

Usage:
    python scripts/build_stlite.py

Output:
    docs/index.html          -- stlite app
    docs/data/data.json      -- game data
    docs/images/64/*.png     -- thumbnail images
    docs/images/256/*.png    -- hero card images
"""

import json
import os
import shutil
from pathlib import Path

# --- Paths ---
ROOT = Path(__file__).resolve().parent.parent
APP_PY = ROOT / "app" / "app.py"
DATA_PY = ROOT / "ultra_satisfactory" / "data.py"
DATA_JSON = ROOT / "data" / "data.json"
IMAGES_DIR = ROOT / "app" / "static" / "images"
DOCS_DIR = ROOT / "docs"

# stlite CDN version
STLITE_VERSION = "1.3.0"
STLITE_JS = f"https://cdn.jsdelivr.net/npm/@stlite/browser@{STLITE_VERSION}/build/stlite.js"
STLITE_CSS = f"https://cdn.jsdelivr.net/npm/@stlite/browser@{STLITE_VERSION}/build/stlite.css"


def read_file(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def adapt_data_py(source: str) -> str:
    """Adapt data.py for stlite runtime.

    Changes:
    - Replace filesystem-based load_data() with one that reads from a known path
    - Replace local_image_url() to return relative URLs for stlite-served files
    - Remove _find_images_base() filesystem walk (no real filesystem in stlite)
    """
    # We'll write a completely clean version for stlite that keeps the same
    # function signatures but uses stlite-compatible paths.
    return '''"""Load and parse data.json — stlite-adapted version."""

import json
from pathlib import Path

__all__ = ['load_data', 'wiki_image_url', 'image_slug', 'local_image_url', 'get_item_recipe', 'list_items']


def load_data(data_path=None):
    """Load data.json from the stlite virtual filesystem."""
    if data_path is None:
        data_path = "/home/pyodide/data/data.json"
    with open(data_path, encoding="utf-8") as f:
        return json.load(f)


def wiki_image_url(item_name: str, size: int = 128) -> str:
    slug = item_name.replace(' ', '_')
    return f'https://satisfactory.wiki.gg/images/thumb/{slug}.png/{size}px-{slug}.png'


def image_slug(name: str) -> str:
    return name.replace(' ', '_').replace("'", '_').replace(':', '_')


# ⚡ In stlite, images are served as static files from the docs/ directory.
# We use relative URLs that GitHub Pages will serve.
_CACHED_SIZES = [256, 64]


def local_image_url(item_name: str, size: int = 64) -> str:
    """Return relative URL for stlite/GitHub Pages hosted images."""
    slug = image_slug(item_name)
    # In stlite, we mount images at /home/pyodide/images/{size}/{slug}.png
    # but we serve them via relative URLs from the HTML page.
    # Use the wiki.gg fallback for simplicity — images load from CDN.
    # For offline/faster loading, we could serve from docs/ but that requires
    # the stlite app to know its base URL.
    #
    # Strategy: try to reference images via a relative path that GitHub Pages serves.
    # The HTML page is at docs/index.html, images at docs/images/{size}/{slug}.png
    # So the relative URL is: images/{size}/{slug}.png
    best = None
    for s in _CACHED_SIZES:
        if s >= size:
            best = s
        elif best is None:
            best = s
    if best is None:
        best = 64
    return f'images/{best}/{slug}.png'


def get_item_recipe(item_name: str, data: dict, alternate: bool = False):
    items = data.get('items', {})
    recipes = data.get('recipes', {})
    buildings = data.get('buildings', {})

    item_key = None
    item_data = None
    for key, item in items.items():
        if item.get('name', '').lower() == item_name.lower():
            item_key = key
            item_data = item
            break
    if item_key is None:
        return None

    recipe_data = None
    for recipe in recipes.values():
        if not recipe.get('inMachine', False):
            continue
        products = recipe.get('products', [])
        if not any(p['item'] == item_key for p in products):
            continue
        is_alt = recipe.get('alternate', False)
        if is_alt == alternate:
            recipe_data = recipe
            break

    if recipe_data is None:
        return None

    cycle_time = recipe_data.get('time', 1)
    cycles_per_min = 60.0 / cycle_time

    def resolve_ingredient(entry):
        ref_key = entry['item']
        amount = entry['amount']
        ref_item = items.get(ref_key) or data.get('resources', {}).get(ref_key, {})
        return {
            'name': ref_item.get('name', ref_key),
            'amount': amount,
            'rate_per_min': round(amount * cycles_per_min, 4),
        }

    ingredients = [resolve_ingredient(e) for e in recipe_data.get('ingredients', [])]
    products = [resolve_ingredient(e) for e in recipe_data.get('products', [])]

    produced_in = recipe_data.get('producedIn', [])
    machine_key = produced_in[0] if produced_in else None
    machine_data = buildings.get(machine_key, {}) if machine_key else {}
    machine_name = machine_data.get('name', machine_key or 'Unknown')
    machine_power = machine_data.get('metadata', {}).get('powerConsumption', 0)

    return {
        'name': item_data.get('name', item_name),
        'description': item_data.get('description', ''),
        'image_url': local_image_url(item_data.get('name', item_name)),
        'ingredients': ingredients,
        'products': products,
        'machine': machine_name,
        'machine_power': machine_power,
        'cycle_time': cycle_time,
        'recipe_name': recipe_data.get('name', ''),
        'alternate': recipe_data.get('alternate', False),
    }


def list_items(data: dict, size: int = 40):
    resource_keys = set(data.get('resources', {}).keys())
    items = [
        {
            'class_key': key,
            'name': item.get('name', key),
            'image_url': local_image_url(item.get('name', key)),
        }
        for key, item in data.get('items', {}).items()
        if key not in resource_keys
    ]
    return sorted(items, key=lambda x: x['name'].lower())
'''


def adapt_app_py(source: str) -> str:
    """Adapt app.py for stlite runtime.

    Changes:
    - Remove sys.path manipulation (data.py is mounted as a file directly)
    - Remove _patch_streamlit_index() (no server-side index.html in stlite)
    - Change import to use the stlite-mounted data module
    """
    lines = source.split('\n')
    adapted = []
    skip_patch = False
    skip_patch_call = False

    for line in lines:
        # Remove sys.path manipulation and related imports
        if 'sys.path.insert' in line:
            continue
        if "import sys" in line and "from pathlib" not in line:
            continue
        if "from pathlib import Path" in line:
            continue

        # Remove stale comments about sys.path or index.html patching
        stripped = line.strip()
        if stripped == '# Add project root to path so we can import ultra_satisfactory':
            continue
        if '# ⚡ Auto-patch Streamlit' in stripped:
            skip_patch = True
            continue
        if skip_patch and stripped.startswith('#'):
            continue  # skip continuation comment lines
        if skip_patch and stripped == '':
            skip_patch = False
            continue

        # Remove the _patch_streamlit_index function definition + call
        if 'def _patch_streamlit_index' in line:
            skip_patch = True
            continue
        if skip_patch:
            if line.startswith('_patch_streamlit_index()'):
                skip_patch = False
                continue
            # Still inside function body (indented)
            if line.startswith('    ') or line.strip() == '':
                continue
            else:
                # End of function definition, but haven't seen the call yet
                if '_patch_streamlit_index()' in line:
                    skip_patch = False
                    continue
                skip_patch = False
                # This line is NOT part of the patch function, keep it

        # Skip standalone _patch_streamlit_index() call if it wasn't caught above
        if line.strip() == '_patch_streamlit_index()':
            continue

        # Fix import — in stlite, data.py is mounted alongside app.py
        if 'from ultra_satisfactory.data import' in line:
            line = line.replace('from ultra_satisfactory.data import', 'from data import')

        # Strip _default_tab line (stlite doesn't support st.tabs(default=))
        if line.strip().startswith('_default_tab ='):
            continue

        # Strip default= kwarg from st.tabs() call (may be on its own line)
        if 'default=_default_tab' in line:
            import re
            line = re.sub(r',?\s*default=_default_tab', '', line)
            # If the line is now just whitespace or empty brackets, skip it
            if not line.strip() or line.strip() in (')', ''):
                continue

        adapted.append(line)

    return '\n'.join(adapted)


def escape_for_js(s: str) -> str:
    """Escape a Python source string for embedding in a JS template literal."""
    return s.replace('\\', '\\\\').replace('`', '\\`').replace('${', '\\${')


def build_index_html(app_code: str, data_module_code: str) -> str:
    """Generate the docs/index.html with stlite mount() call."""

    app_escaped = escape_for_js(app_code)
    data_mod_escaped = escape_for_js(data_module_code)

    return f'''<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <meta name="color-scheme" content="dark">
    <title>ULTRA SATISFACTORY</title>
    <style>
        html, body {{
            background: #000 !important;
            margin: 0;
            padding: 0;
        }}
        /* Loading screen */
        #loading {{
            position: fixed;
            inset: 0;
            background: #000;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            z-index: 9999;
            font-family: 'Share Tech Mono', monospace;
            color: #555;
            letter-spacing: 0.3em;
            font-size: 0.85rem;
        }}
        #loading .spinner {{
            width: 48px;
            height: 48px;
            border: 3px solid #333;
            border-top-color: #00cfff;
            border-radius: 50%;
            animation: spin 1.5s linear infinite;
            margin-bottom: 1.5rem;
        }}
        @keyframes spin {{
            to {{ transform: rotate(360deg); }}
        }}
        #loading .status {{
            color: #444;
            font-size: 0.7rem;
            margin-top: 0.5rem;
        }}
    </style>
    <link
        rel="stylesheet"
        href="{STLITE_CSS}"
    />
</head>
<body>
    <div id="loading">
        <div class="spinner"></div>
        <div>INITIALIZING CONTROL TERMINAL</div>
        <div class="status">loading python runtime...</div>
    </div>
    <div id="root"></div>
    <script type="module">
        import {{ mount }} from "{STLITE_JS}";

        // Hide loading screen once stlite is ready
        const observer = new MutationObserver(() => {{
            const app = document.querySelector('[data-testid="stApp"]');
            if (app) {{
                document.getElementById('loading').style.display = 'none';
                observer.disconnect();
            }}
        }});
        observer.observe(document.getElementById('root'), {{ childList: true, subtree: true }});

        mount(
            {{
                requirements: ["pandas", "streamlit-aggrid"],
                entrypoint: "app.py",
                files: {{
                    "app.py": `{app_escaped}`,
                    "data.py": `{data_mod_escaped}`,
                    "data/data.json": {{
                        url: "./data/data.json",
                    }},
                }},
                streamlitConfig: {{
                    "theme.backgroundColor": "#000000",
                    "theme.secondaryBackgroundColor": "#0f0f23",
                    "theme.primaryColor": "#e8d44d",
                    "theme.textColor": "#eeeeee",
                    "theme.font": "monospace",
                    "client.toolbarMode": "viewer",
                }},
            }},
            document.getElementById("root"),
        );
    </script>
</body>
</html>'''


def copy_assets():
    """Copy data.json and images into docs/."""
    # data/data.json -> docs/data/data.json
    docs_data = DOCS_DIR / "data"
    docs_data.mkdir(parents=True, exist_ok=True)
    shutil.copy2(DATA_JSON, docs_data / "data.json")
    print(f"  Copied data.json ({DATA_JSON.stat().st_size / 1024:.0f} KB)")

    # images -> docs/images/
    docs_images = DOCS_DIR / "images"
    if docs_images.exists():
        shutil.rmtree(docs_images)

    if IMAGES_DIR.exists():
        shutil.copytree(IMAGES_DIR, docs_images)
        # Count files
        count = sum(1 for _ in docs_images.rglob("*.png"))
        total_kb = sum(f.stat().st_size for f in docs_images.rglob("*.png")) / 1024
        print(f"  Copied {count} images ({total_kb:.0f} KB)")
    else:
        print("  WARNING: No images directory found at", IMAGES_DIR)


def main():
    print("Building stlite deployment...")
    print(f"  Source: {ROOT}")
    print(f"  Output: {DOCS_DIR}")

    # Ensure docs/ exists
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    # Read source files
    app_source = read_file(APP_PY)
    data_source = read_file(DATA_PY)

    # Adapt for stlite
    print("  Adapting data.py for stlite...")
    stlite_data_py = adapt_data_py(data_source)

    print("  Adapting app.py for stlite...")
    stlite_app_py = adapt_app_py(app_source)

    # Generate index.html
    print("  Generating index.html...")
    html = build_index_html(stlite_app_py, stlite_data_py)
    (DOCS_DIR / "index.html").write_text(html, encoding="utf-8")
    print(f"  Written index.html ({len(html) / 1024:.0f} KB)")

    # Copy assets
    print("  Copying assets...")
    copy_assets()

    print("Done! Deploy docs/ to GitHub Pages.")


if __name__ == "__main__":
    main()
