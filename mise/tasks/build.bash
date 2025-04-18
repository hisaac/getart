#!/usr/bin/env bash
set -euo pipefail

#MISE description="Build the project"
#USAGE flag "--configuration <configuration>" {
#USAGE 	choices "debug" "release"
#USAGE 	default "release"
#USAGE 	help    "The configuration to build the project with"
#USAGE }

swift build --configuration "$usage_configuration"
