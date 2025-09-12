#!/usr/bin/env bash
#MISE description="Build the project"
#USAGE flag "--configuration <configuration>" {
#USAGE 	choices "debug" "release"
#USAGE 	default "release"
#USAGE 	help    "The configuration to build the project with"
#USAGE }

set -euo pipefail

swift build --configuration "$usage_configuration" | xcbeautify
