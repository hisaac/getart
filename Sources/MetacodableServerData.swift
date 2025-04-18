import Foundation
import MetaCodable

@Codable
struct MetaCodableServerData {
	@CodedAt("data", "sections")
	let sections: [Section]

	@Codable
	struct Section {
		let containerArtwork: ImageArtwork?
		let items: [Item]

		@Codable
		struct ImageArtwork {
			@CodedAt("dictionary", "width")
			let width: Int

			@CodedAt("dictionary", "height")
			let height: Int

			@CodedAt("dictionary", "url")
			let encodedURL: String
		}

		@Codable
		struct Item {
			let videoArtwork: VideoArtwork?

			@Codable
			struct VideoArtwork {
				@CodedAt("dictionary", "motionDetailSquare", "video")
				let video: String
			}
		}
	}
}

extension MetaCodableServerData {
	func imageArtworkURL() async throws -> URL? {
		let sectionWithArtwork = sections.first { $0.containerArtwork != nil }
		return sectionWithArtwork?.containerArtwork?.url()
	}

	func videoArtworkURL() async throws -> URL? {
		var videoArtworkURL: URL?
		for section in sections {
			for item in section.items {
				if let videoArtwork = item.videoArtwork {
					videoArtworkURL = try await videoArtwork.url()
					break
				}
			}
		}
		return videoArtworkURL
	}
}

extension MetaCodableServerData.Section.ImageArtwork {
	func url() -> URL? {
		URLResolver.imageURL(from: encodedURL, width: width, height: height)
	}
}

extension MetaCodableServerData.Section.Item.VideoArtwork {
	func url() async throws -> URL? {
		try await URLResolver.videoURL(from: video)
	}
}
