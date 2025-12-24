from __future__ import annotations

from pathlib import Path

from getart.core import ServerData

FIXTURES = Path(__file__).parent / "data"


def load_fixture(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


def test_image_artwork_url() -> None:
    server_data = ServerData.from_json(
        load_fixture("test-json-no-video-only-used-data.json")
    )
    assert server_data.image_artwork_url() == (
        "https://is1-ssl.mzstatic.com/image/thumb/Music211/v4/c5/9a/d0/"
        "c59ad049-d5a4-8df2-8564-238472cf497a/24UMGIM28458.rgb.jpg/3000x3000bb.jpg"
    )


def test_video_playlist_url() -> None:
    server_data = ServerData.from_json(
        load_fixture("test-json-with-video-only-used-data.json")
    )
    assert (
        server_data.video_playlist_url()
        == "https://mvod.itunes.apple.com/itunes-assets/HLSVideo221/v4/41/85/ad/"
        "4185ad71-e897-fe37-6193-a7dc7abb13f0/P837475808_default.m3u8"
    )


def test_artist_name() -> None:
    server_data = ServerData.from_json(load_fixture("test-json-with-video.json"))
    assert server_data.artist_name() == "Willie Nelson"


def test_album_name() -> None:
    server_data = ServerData.from_json(load_fixture("test-json-with-video.json"))
    assert server_data.album_name() == "The Border"
