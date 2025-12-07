#!/usr/bin/env bash
#MISE description="Nuke build artifacts and Python caches"
#MISE depends=["clean"]

set -euxo pipefail

rm -rf .venv
uv cache prune
