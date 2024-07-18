import Foundation
import M3U8Parser

// swiftlint:disable nesting

typealias ServerData = [ServerDatum]

struct ServerDatum: Decodable {
	let data: DataClass

	struct DataClass: Decodable {
		let sections: [Section]

		struct Section: Decodable {
			let items: [Item]

			struct Item: Decodable {
				let artwork: Artwork?
				let videoArtwork: VideoArtwork?
			}
		}
	}
}

public struct Artwork: Decodable {
	let dictionary: ArtworkDictionary

	struct ArtworkDictionary: Decodable {
		let width: Int
		let url: String
		let height: Int
	}
}

public struct VideoArtwork: Decodable {
	let dictionary: VideoArtworkDictionary

	struct VideoArtworkDictionary: Decodable {
		let motionDetailSquare: MotionDetailSquare

		struct MotionDetailSquare: Decodable {
			let video: String
		}
	}
}

public extension [ServerDatum] {
	var artwork: Artwork? {
		first?.data.sections.first?.items.first?.artwork
	}

	var videoArtwork: VideoArtwork? {
		first?.data.sections.first?.items.first?.videoArtwork
	}
}

extension Artwork {
	var url: URL? {
		return dictionary.formattedURL
	}
}

extension Artwork.ArtworkDictionary {
	var formattedURL: URL? {
		let urlString = url
			.replacingOccurrences(of: "{w}", with: "\(width)")
			.replacingOccurrences(of: "{h}", with: "\(height)")
			.replacingOccurrences(of: "{f}", with: "jpg")
		return URL(string: urlString)
	}
}

extension VideoArtwork {
	func url() async throws -> URL? {
		guard let playlistURL else { return nil }
		return try await VideoArtwork.parseM3U8Playlist(playlistURL)
	}

	var playlistURL: URL? {
		URL(string: dictionary.motionDetailSquare.video)
	}

	private static func parseM3U8Playlist(_ playlistURL: URL) async throws -> URL? {
		guard
			let model = try await (playlistURL as NSURL).m3u_loadAsyncCompletion(),
			let masterPlaylist = model.masterPlaylist, // swiftlint:disable:this inclusive_language
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

// swiftlint:enable nesting
