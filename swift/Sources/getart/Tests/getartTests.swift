import XCTest
@testable import getart

final class getartTests: XCTestCase {
	func testJSONParsing_WithVideo() async throws {
		// given
		let testHarnessURL = try XCTUnwrap(
			Bundle.testModule().url(forResource: "test-json-with-video", withExtension: "json")
		)
		let testHarnessData = try Data(contentsOf: testHarnessURL)

		// when
		let serverData = try JSONDecoder().decode(ServerData.self, from: testHarnessData)

		// then
		let artwork = try XCTUnwrap(serverData.artwork)
		XCTAssertNotNil(artwork.url)
		let videoArtwork = try XCTUnwrap(serverData.videoArtwork)
		let videoArtworkURL = try await videoArtwork.url()
		XCTAssertNotNil(videoArtworkURL)
	}

	func testJSONParsing_NoVideo() async throws {
		// given
		let testHarnessURL = try XCTUnwrap(
			Bundle.testModule().url(forResource: "test-json-no-video", withExtension: "json")
		)
		let testHarnessData = try Data(contentsOf: testHarnessURL)

		// when
		let serverData = try JSONDecoder().decode(ServerData.self, from: testHarnessData)

		// then
		let artwork = try XCTUnwrap(serverData.artwork)
		XCTAssertNotNil(artwork.url)
		XCTAssertNil(serverData.videoArtwork)
	}
}

fileprivate extension Foundation.Bundle {
	/// Finds and returns the `Bundle` for the module
	///
	/// Annoyingly, the `SwiftSoup` library includes a static variable of `module` and because it is marked `internal`
	/// instead of `private`, Xcode tries to use that variable when attempting to reference `Bundle.module` directly.
	/// So this function works around that by running down the tree to find the `Bundle` for this test module.
	///
	/// - Returns: The `Bundle` for this module
	static func testModule() throws -> Bundle {
		let mainBundle = try XCTUnwrap(Bundle(identifier: "getartTests"))
		let moduleBundleURL = try XCTUnwrap(mainBundle.url(forResource: "getart_getartTests", withExtension: "bundle"))
		let moduleBundle = try XCTUnwrap(Bundle(url: moduleBundleURL))
		return moduleBundle
	}
}
