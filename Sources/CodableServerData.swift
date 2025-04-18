import Foundation

struct CodableServerData: Decodable {
	let data: DataClass

	struct DataClass: Decodable {
		let sections: [Section]

		struct Section: Decodable {
			let items: [Item]

			struct Item: Decodable {
				let artwork: Artwork?
				let videoArtwork: VideoArtwork?

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
			}
		}
	}
}

extension CodableServerData {
	func imageArtworkURL() async throws -> URL? {
		data.sections.first?.items.first?.artwork?.dictionary.imageURL()
	}

	func videoArtworkURL() async throws -> URL? {
		try await data.sections.first?.items.first?.videoArtwork?.dictionary.motionDetailSquare.videoURL()
	}
}

extension CodableServerData.DataClass.Section.Item.Artwork.ArtworkDictionary {
	func imageURL() -> URL? {
		URLResolver.imageURL(from: url, width: width, height: height)
	}
}

extension CodableServerData.DataClass.Section.Item.VideoArtwork.VideoArtworkDictionary.MotionDetailSquare {
	func videoURL() async throws -> URL? {
		try await URLResolver.videoURL(from: video)
	}
}
