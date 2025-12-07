#!/usr/bin/env bash
#MISE description="Run the project's tests"

set -euo pipefail

PYTHONPATH="${PYTHONPATH:+${PYTHONPATH}:}$(pwd)/src" uv run pytest
