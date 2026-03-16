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

# ---------------------------------------------------------------------------
# Container image — Python 3.11, same deps as requirements.txt
# ---------------------------------------------------------------------------
image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "streamlit==1.45.1",
        "streamlit-aggrid==1.2.1.post2",
        "pandas",
    )
)

# ---------------------------------------------------------------------------
# Mount the entire repo into /app inside the container.
# Modal mounts are read-only snapshots uploaded at deploy time.
# We mount selectively to keep the image small and avoid uploading .git etc.
# ---------------------------------------------------------------------------
repo_root = Path(__file__).parent

mount = modal.Mount.from_local_dir(
    repo_root,
    remote_path="/app",
    condition=lambda p: (
        # include everything except heavy/unnecessary dirs
        not any(
            part in Path(p).parts
            for part in [".git", "__pycache__", ".mypy_cache", "docs", "nbs", "_proc",
                         "ultra_satisfactory.egg-info", "node_modules"]
        )
    ),
)

# ---------------------------------------------------------------------------
# Modal app
# ---------------------------------------------------------------------------
app = modal.App(name="ultra-satisfactory", image=image)


@app.function(mounts=[mount], allow_concurrent_inputs=100)
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
