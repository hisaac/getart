#!/usr/bin/env bash
#MISE description="Run the project's tests"

set -euxo pipefail

swift test
