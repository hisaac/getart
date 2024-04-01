// swift-tools-version: 5.10

import PackageDescription

let package = Package(
	name: "getart",
	platforms: [.macOS(.v14)],
	dependencies: [
		.package(url: "https://github.com/M3U8Kit/M3U8Parser.git", from: "1.1.0"),
		.package(url: "https://github.com/scinfu/SwiftSoup.git", from: "2.7.2"),
		.package(url: "https://github.com/realm/SwiftLint.git", from: "0.54.0"),
	],
	targets: [
		.executableTarget(
			name: "getart",
			dependencies: [
				.product(name: "M3U8Parser", package: "M3U8Parser"),
				.product(name: "SwiftSoup", package: "SwiftSoup"),
			],
			path: "Sources/getart/Sources",
			plugins: [
				.plugin(name: "SwiftLintPlugin", package: "SwiftLint"),
			]
		),
		.testTarget(
			name: "getartTests",
			dependencies: [
				.target(name: "getart"),
			],
			path: "Sources/getart/Tests",
			resources: [
				.copy("test-data"),
			],
			plugins: [
				.plugin(name: "SwiftLintPlugin", package: "SwiftLint"),
			]
		),
	]
)
