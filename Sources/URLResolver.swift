import Foundation
import M3U8Parser

enum URLResolver {
	static func imageURL(from encodedURL: String, width: Int, height: Int) -> URL? {
		guard
			encodedURL.contains("{w}"),
			encodedURL.contains("{h}"),
			encodedURL.contains("{f}")
		else {
			return nil
		}
		let urlString = encodedURL
			.replacingOccurrences(of: "{w}", with: "\(width)")
			.replacingOccurrences(of: "{h}", with: "\(height)")
			.replacingOccurrences(of: "{f}", with: "jpg")
		return URL(string: urlString)
	}

	static func videoURL(from playlistURL: String) async throws -> URL? {
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
