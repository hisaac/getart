import Foundation
import M3U8Parser
import SwiftSoup

enum getartError: Error {
	case invalidURL
	case dataToStringError
	case jsonDataToStringError
	case jsonSerializationError
}

typealias JSONDict = [String: Any]
typealias JSONArray = [Any]

@main
struct getart {
	static func main() async throws {
		let urlString = CommandLine.arguments[1]
		guard let url = URL(string: urlString) else {
			throw getartError.invalidURL
		}

		let (data, _) = try await URLSession.shared.data(from: url)
		guard let html = String(data: data, encoding: .utf8) else {
			throw getartError.dataToStringError
		}
		let doc = try SwiftSoup.parse(html)

		guard
			let serverDataJSONElement = try doc.getElementById("serialized-server-data")
		else {
			throw getartError.jsonDataToStringError
		}

		let serverDataJSONString = try serverDataJSONElement.html()
		guard
			let serverDataJSONData = serverDataJSONString.data(using: .utf8)
		else {
			throw getartError.jsonSerializationError
		}

		let serverDataJSON = try JSONSerialization.jsonObject(with: serverDataJSONData)
		guard
			let serverDataDict = (serverDataJSON as? [JSONDict])?.first,
			let data = serverDataDict["data"] as? JSONDict,
			let sections = data["sections"] as? JSONArray,
			let items = (sections.first as? JSONDict)?["items"] as? JSONArray,
			let item = items.first as? JSONDict
		else {
			throw getartError.jsonSerializationError
		}

		let artworkURL = try parseArtworkURL(item)
		print("Artwork URL:", artworkURL)

		let videoArtworkPlaylistURL = try parseVideoArtworkPlaylistURL(item)
		print("Video Artwork Playlist URL:", videoArtworkPlaylistURL)

		let videoURL = try await parseM3U8Playlist(videoArtworkPlaylistURL)
		print("Video URL:", videoURL)
	}

	private static func parseArtworkURL(_ item: JSONDict) throws -> URL {
		guard
			let artwork = item["artwork"] as? JSONDict,
			let artworkDict = artwork["dictionary"] as? JSONDict,
			let artworkWidth = artworkDict["width"] as? Int,
			let artworkHeight = artworkDict["height"] as? Int,
			let artworkURLString = artworkDict["url"] as? String
		else {
			throw getartError.jsonSerializationError
		}

		let constructedArtworkURLString = artworkURLString
			.replacingOccurrences(of: "{w}", with: "\(artworkWidth)")
			.replacingOccurrences(of: "{h}", with: "\(artworkHeight)")
			.replacingOccurrences(of: "{f}", with: "jpg")

		guard let artworkURL = URL(string: constructedArtworkURLString) else {
			throw getartError.invalidURL
		}

		return artworkURL
	}

	private static func parseVideoArtworkPlaylistURL(_ item: JSONDict) throws -> URL {
		guard
			let videoArtwork = item["videoArtwork"] as? JSONDict,
			let videoArtworkDict = videoArtwork["dictionary"] as? JSONDict,
			let motionDetailSquare = videoArtworkDict["motionDetailSquare"] as? JSONDict,
			let videoURLString = motionDetailSquare["video"] as? String
		else {
			throw getartError.jsonSerializationError
		}

		guard let videoArtworkPlaylistURL = URL(string: videoURLString) else {
			throw getartError.invalidURL
		}

		return videoArtworkPlaylistURL
	}

	private static func parseM3U8Playlist(_ playlistURL: URL) async throws -> URL {
		guard
			let model = try await (playlistURL as NSURL).m3u_loadAsyncCompletion(),
			let masterPlaylist = model.masterPlaylist,
			let allStreamURLs = masterPlaylist.allStreamURLs() as? [NSURL]
		else {
			return ""
		}

		guard
			let lastPlaylistURL = allStreamURLs.last,
			let videoModel = try await lastPlaylistURL.m3u_loadAsyncCompletion(),
			let allSegmentURLs = videoModel.mainMediaPl.allSegmentURLs() as? [NSURL],
			let fullURLSegments = allSegmentURLs.first,
			let segments = fullURLSegments.absoluteString?.split(separator: " -- "),
			let videoURL = URL(string: segments.joined())
		else {
			return ""
		}

		return videoURL
	}
}

extension URL: ExpressibleByStringLiteral {
	public init(stringLiteral value: StaticString) {
		guard let url = URL(string: "\(value)") else {
			preconditionFailure()
		}
		self = url
	}
}
