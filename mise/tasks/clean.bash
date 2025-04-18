#!/usr/bin/env bash
#MISE description="Clean the project"

set -euo pipefail

killall -q Xcode || true
swift package clean
rm -rf .build
rm -rf DerivedData
rm -rf Package.resolved
