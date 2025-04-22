import Foundation
import M3U8Parser

struct ServerData {
	let jsonObject: Any

	init(from jsonData: Data) throws {
		jsonObject = try JSONSerialization.jsonObject(with: jsonData, options: [])
	}

	func imageArtworkURL() -> URL? {
		guard
			let jsonArray = jsonObject as? [[String: Any]],
			let firstObject = jsonArray.first,
			let data = firstObject["data"] as? [String: Any],
			let sections = data["sections"] as? [[String: Any]],
			let section = sections.first(where: { $0["containerArtwork"] != nil }),
			let containerArtwork = section["containerArtwork"] as? [String: Any],
			let dictionary = containerArtwork["dictionary"] as? [String: Any],
			let width = dictionary["width"] as? Int,
			let height = dictionary["height"] as? Int,
			let encodedURL = dictionary["url"] as? String
		else {
			return nil
		}

		let urlString = encodedURL
			.replacingOccurrences(of: "{w}", with: "\(width)")
			.replacingOccurrences(of: "{h}", with: "\(height)")
			.replacingOccurrences(of: "{f}", with: "jpg")
		return URL(string: urlString)
	}

	func videoArtworkURL() async throws -> URL? {
		guard
			let jsonArray = jsonObject as? [[String: Any]],
			let firstObject = jsonArray.first,
			let data = firstObject["data"] as? [String: Any],
			let sections = data["sections"] as? [[String: Any]]
		else {
			return nil
		}

		for section in sections {
			if let items = section["items"] as? [[String: Any]] {
				for item in items {
					if let videoArtwork = item["videoArtwork"] as? [String: Any],
					let dictionary = videoArtwork["dictionary"] as? [String: Any],
					let motionDetailSquare = dictionary["motionDetailSquare"] as? [String: Any],
					let playlistURL = motionDetailSquare["video"] as? String {
						return try await getVideoURL(from: playlistURL)
					}
				}
			}
		}

		return nil
	}

	private func getVideoURL(from playlistURL: String) async throws -> URL? {
		guard
			let playlistURL = URL(string: playlistURL),
			let model = try await (playlistURL as NSURL).m3u_loadAsyncCompletion(),
			let masterPlaylist = model.masterPlaylist,
			let allStreamURLs = masterPlaylist.allStreamURLs() as? [NSURL],
			let lastPlaylistURL = allStreamURLs.last,
			let videoModel = try await lastPlaylistURL.m3u_loadAsyncCompletion(),
			let allSegmentURLs = videoModel.mainMediaPl.allSegmentURLs() as? [NSURL],
			let fullURLSegments = allSegmentURLs.first,
			let segments = fullURLSegments.absoluteString?.split(separator: " -- "),
			let videoURL = URL(string: segments.joined())
		else {
			return nil
		}

		return videoURL
	}
}
