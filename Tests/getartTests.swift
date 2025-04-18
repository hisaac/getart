import Foundation
import Testing
@testable import getart

struct getartTests {

	@Test("JSON parsing with video artwork")
	func testJSONParsingWithVideo() async throws {
		// given
		let testHarnessURL = try #require(
			Bundle.module.url(forResource: "test-json-with-video-only-used-data", withExtension: "json")
		)
		let testHarnessData = try Data(contentsOf: testHarnessURL)
		let expectedResult = URL(string: "https://mvod.itunes.apple.com/itunes-assets/HLSVideo221/v4/4e/11/4c/4e114c89-1dc6-037c-ca65-177bbc9ad720/P837475808_Anull_video_gr698_sdr_2160x2160-.mp4")

		// when
		let serverData = try JSONDecoder().decode([MetaCodableServerData].self, from: testHarnessData)

		// then
		let serverDatum = try #require(serverData.first)
		#expect(try await serverDatum.videoArtworkURL() == expectedResult)
	}

	@Test("JSON parsing without video artwork")
	func testJSONParsingNoVideo() async throws {
		// given
		let testHarnessURL = try #require(
			Bundle.module.url(forResource: "test-json-no-video", withExtension: "json")
		)
		let testHarnessData = try Data(contentsOf: testHarnessURL)
		let expectedResult = URL(string: "https://is1-ssl.mzstatic.com/image/thumb/Music211/v4/c5/9a/d0/c59ad049-d5a4-8df2-8564-238472cf497a/24UMGIM28458.rgb.jpg/3000x3000bb.jpg")

		// when
		let serverData = try JSONDecoder().decode([MetaCodableServerData].self, from: testHarnessData)

		// then
		let serverDatum = try #require(serverData.first)
		#expect(try await serverDatum.imageArtworkURL() == expectedResult)
	}
}
