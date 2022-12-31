// swift-tools-version: 5.7

import PackageDescription

let package = Package(
	name: "getart",
	platforms: [.macOS(.v13)],
	dependencies: [
		.package(url: "https://github.com/M3U8Kit/M3U8Parser.git", from: "1.0.2"),
		.package(url: "https://github.com/scinfu/SwiftSoup.git", from: "2.4.3"),
	],
	targets: [
		.executableTarget(
			name: "getart",
			dependencies: [
				.product(name: "M3U8Parser", package: "M3U8Parser"),
				.product(name: "SwiftSoup", package: "SwiftSoup"),
			]
		),
	]
)
