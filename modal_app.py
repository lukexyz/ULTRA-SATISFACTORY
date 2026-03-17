# ⚡ Modal deployment for ULTRA-SATISFACTORY
#
# Usage:
#   modal serve modal_app.py      # ephemeral — live-reloads on file changes
#   modal deploy modal_app.py     # persistent public URL
#
# Requires:
#   pip install modal
#   modal token new               # one-time auth

import shlex
import subprocess
from pathlib import Path

import modal

repo_root = Path(__file__).parent

# ---------------------------------------------------------------------------
# Container image — Python 3.11, same deps as requirements.txt.
# add_local_dir() copies repo files into the image at build time (Modal 1.x).
# We exclude heavy/generated dirs to keep uploads fast.
# ---------------------------------------------------------------------------
EXCLUDE = {".git", "__pycache__", ".mypy_cache", "docs", "nbs", "_proc",
           "ultra_satisfactory.egg-info", "node_modules"}

def _exclude(relpath: Path) -> bool:
    return any(part in EXCLUDE for part in relpath.parts)

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "streamlit==1.55.0",
        "streamlit-aggrid==1.2.1.post2",
        "pandas",
    )
    .add_local_dir(
        str(repo_root),
        remote_path="/app",
        ignore=_exclude,
    )
    # ⚡ Bake dark-background patch into the image at build time so the very
    # first cold-start request already gets a dark index.html — no white flash.
    # Mirrors the runtime _patch_streamlit_index() in app.py (which stays as
    # a safety net for local dev and is idempotent).
    .run_commands("python /app/scripts/patch_streamlit_index.py")
)

# ---------------------------------------------------------------------------
# Modal app
# ---------------------------------------------------------------------------
app = modal.App(name="ultra-satisfactory", image=image)


@app.function()
@modal.concurrent(max_inputs=100)
@modal.web_server(8000)
def run():
    target = shlex.quote("/app/app/app.py")
    cmd = (
        f"streamlit run {target} "
        f"--server.port 8000 "
        f"--server.address 0.0.0.0 "
        f"--server.enableCORS=false "
        f"--server.enableXsrfProtection=false "
        f"--server.headless=true "
        f"--server.enableStaticServing=true"
    )
    # Run from /app so Streamlit finds .streamlit/config.toml and serves
    # app/static/ at /app/static/<filename> relative to the project root.
    subprocess.Popen(cmd, shell=True, cwd="/app")
