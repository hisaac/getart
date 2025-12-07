#!/usr/bin/env bash
#MISE description="Run the project"
#USAGE arg "<url>" help="The Apple Music URL to get the artwork for"

set -euo pipefail

PYTHONPATH="${PYTHONPATH:+${PYTHONPATH}:}$(pwd)/src" uv run python -m getart.cli "$usage_url"
