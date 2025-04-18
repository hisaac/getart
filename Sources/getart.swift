import Foundation
import SwiftSoup
import AppKit

enum getartError: Error {
	case invalidURL
	case jsonDataToStringError
	case jsonSerializationError
}

@main
struct getart {
	static func main() async throws {
		let urlString = CommandLine.arguments[1]
		guard let url = URL(string: urlString) else {
			throw getartError.invalidURL
		}

		let (data, _) = try await URLSession.shared.data(from: url)
		let html = String(decoding: data, as: UTF8.self)
		let doc = try SwiftSoup.parse(html)
		let serverDataJSONElement = try doc.getElementById("serialized-server-data")

		guard let serverDataJSONElement else {
			throw getartError.jsonDataToStringError
		}

		let serverDataJSONString = try serverDataJSONElement.html()
		let serverDataJSONData = serverDataJSONString.data(using: .utf8)

		guard let serverDataJSONData else {
			throw getartError.jsonSerializationError
		}

		let serverData = try JSONDecoder().decode([MetaCodableServerData].self, from: serverDataJSONData).first

		if let artworkURL = try await serverData?.imageArtworkURL() {
			print("Opening artwork URL:", artworkURL)
			NSWorkspace.shared.open(artworkURL)
		}

		if let videoURL = try await serverData?.videoArtworkURL() {
			print("Opening video URL:", videoURL)
			NSWorkspace.shared.open(videoURL)
		}
	}
}
