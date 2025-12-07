#!/usr/bin/env bash
#MISE description="Remove build artifacts"

set -euxo pipefail

rm -rf .pytest_cache
rm -rf build dist
rm -rf *.egg-info
find . -name '__pycache__' -type d -prune -exec rm -rf {} +
