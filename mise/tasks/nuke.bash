#!/usr/bin/env bash
#MISE description="Nuke the project and global caches"
#MISE depends=["clean"]

set -euo pipefail

rm -rf ~/Library/Developer/Xcode/DerivedData
rm -rf ~/Library/Caches/org.swift.swiftpm
rm -rf ~/Library/Preferences/org.swift.swiftpm.plist
