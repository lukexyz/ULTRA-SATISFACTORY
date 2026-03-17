# ⚡ Patch Streamlit's index.html to prevent white flash on cold start.
# Run at Modal image build time via .run_commands() in modal_app.py.
# Injects dark background + color-scheme meta into <head> before any
# JS/CSS loads. Idempotent — safe to run multiple times.

from pathlib import Path

import streamlit as st

INJECT = (
    '<meta name="color-scheme" content="dark">'
    '<style>html,body{background:#000!important}</style>'
)

index = Path(st.__file__).parent / "static" / "index.html"
html = index.read_text()

if INJECT not in html:
    html = html.replace("<head>\n", f"<head>\n    {INJECT}\n", 1)
    index.write_text(html)
    print(f"Patched {index}")
else:
    print(f"Already patched — skipping {index}")
