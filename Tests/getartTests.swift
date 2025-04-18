import Foundation
import Testing
@testable import getart

struct getartTests {
	@Test("JSON parsing with video artwork")
	func testJSONParsingWithVideo() async throws {
		// given
		let testHarnessURL = try #require(Bundle.module.url(forResource: "test-json-with-video", withExtension: "json"))
		let testHarnessData = try Data(contentsOf: testHarnessURL)

		// when
		let serverData = try JSONDecoder().decode(ServerData.self, from: testHarnessData)

		// then
		let artwork = try #require(serverData.artwork)
		#expect(artwork.url != nil)

		let videoArtwork = try #require(serverData.videoArtwork)
		let videoArtworkURL = try await videoArtwork.url()
		#expect(videoArtworkURL != nil)
	}

	@Test("JSON parsing without video artwork")
	func testJSONParsingNoVideo() async throws {
		// given
		let testHarnessURL = try #require(Bundle.module.url(forResource: "test-json-no-video", withExtension: "json"))
		let testHarnessData = try Data(contentsOf: testHarnessURL)

		// when
		let serverData = try JSONDecoder().decode(ServerData.self, from: testHarnessData)

		// then
		let artwork = try #require(serverData.artwork)
		#expect(artwork.url != nil)
		#expect(serverData.videoArtwork == nil)
	}
}
