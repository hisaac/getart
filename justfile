# justfile documentation: https://just.systems/man/en/

project_root := justfile_directory()
config_dir   := project_root / ".config"

default: open
reset: nuke open

open: bootstrap
	xcrun xed "{{ project_root }}/Package.swift"

bootstrap:
	xcodes select "$(cat "{{ config_dir }}/.xcode-version")"

clean:
	killall -q Xcode || true
	swift package clean
	rm -rf .build
	rm -rf .swiftpm
	rm -rf Package.resolved

nuke: clean
	rm -rf $HOME/Library/Developer/Xcode/DerivedData
	rm -rf $HOME/Library/Caches/org.swift.swiftpm
	rm -rf $HOME/Library/org.swift.swiftpm
