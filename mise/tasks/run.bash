#!/usr/bin/env bash
#MISE description="Run the project"
#USAGE arg "<url>" help="The Apple Music URL to get the artwork for"

set -euxo pipefail

swift run getart "$usage_url"
