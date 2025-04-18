#!/usr/bin/env bash
#MISE description="Clean the project"

set -euxo pipefail

killall -q Xcode || true
swift package clean
rm -rf .build
rm -rf DerivedData
rm -rf Package.resolved
