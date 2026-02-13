from __future__ import annotations

from pathlib import Path

from getart.core import ServerData


FIXTURES = Path(__file__).parents[1] / "data"


def load_fixture(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


def test_image_artwork_url() -> None:
    server_data = ServerData.from_json(
        load_fixture("test-json-with-video-only-used-data.json")
    )
    assert server_data.image_artwork_url() == (
        "https://is1-ssl.mzstatic.com/image/thumb/Music211/v4/17/cb/e5/"
        "17cbe588-a6c3-d5eb-94d8-ed1aa53e1d5e/196871846042.jpg/4000x4000bb.jpg"
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
