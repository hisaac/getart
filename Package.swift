// swift-tools-version: 6.1

import PackageDescription

let package = Package(
	name: "getart",
	platforms: [.macOS(.v15)],
	products: [
		.executable(name: "getart", targets: ["getart"]),
	],
	dependencies: [
		.package(url: "https://github.com/M3U8Kit/M3U8Parser.git", from: "1.1.0"),
		.package(url: "https://github.com/scinfu/SwiftSoup.git", from: "2.8.7"),
		.package(url: "https://github.com/SwiftyLab/MetaCodable.git", from: "1.4.0"),
	],
	targets: [
		.executableTarget(
			name: "getart",
			dependencies: [
				.byName(name: "M3U8Parser"),
				.byName(name: "SwiftSoup"),
				.byName(name: "MetaCodable"),
			],
			cSettings: [
				// Suppresses the warning about the incomplete umbrella header in the M3U8Parser package
				.unsafeFlags(["-Wno-incomplete-umbrella"])
			]
		),
		.testTarget(
			name: "getartTests",
			dependencies: [
				.target(name: "getart"),
			],
			resources: [
				.process("Resources"),
			]
		),
	]
)
