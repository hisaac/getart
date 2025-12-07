from __future__ import annotations

from pathlib import Path

import httpx

from getart.core import ArtworkAssets, fetch_artwork_assets


FIXTURES = Path(__file__).parent / "data"


def load_fixture(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


def test_fetch_artwork_assets_with_video() -> None:
    page_url = "https://music.apple.com/album/example-album"
    json_payload = load_fixture("test-json-with-video-only-used-data.json")
    html = f"<html><body><div id='serialized-server-data'>{json_payload}</div></body></html>"

    master_manifest = """#EXTM3U
#EXT-X-STREAM-INF:BANDWIDTH=1000000
P837475808_variant.m3u8
"""
    variant_manifest = """#EXTM3U
#EXT-X-MAP:URI="P837475808_Anull_video_gr698_sdr_2160x2160-.mp4"
"""

    def handler(request: httpx.Request) -> httpx.Response:  # type: ignore[override]
        if request.url == httpx.URL(page_url):
            return httpx.Response(200, text=html, headers={"Content-Type": "text/html"})
        if request.url.host == "mvod.itunes.apple.com" and request.url.path.endswith("default.m3u8"):
            return httpx.Response(
                200,
                text=master_manifest,
                headers={"Content-Type": "application/vnd.apple.mpegurl"},
            )
        if request.url.host == "mvod.itunes.apple.com" and request.url.path.endswith("variant.m3u8"):
            return httpx.Response(
                200,
                text=variant_manifest,
                headers={"Content-Type": "application/vnd.apple.mpegurl"},
            )
        raise AssertionError(f"Unhandled request: {request.url}")

    transport = httpx.MockTransport(handler)
    assets: ArtworkAssets = fetch_artwork_assets(page_url, transport=transport)

    assert assets.image_url == (
        "https://is1-ssl.mzstatic.com/image/thumb/Music211/v4/c5/9a/d0/"
        "c59ad049-d5a4-8df2-8564-238472cf497a/24UMGIM28458.rgb.jpg/3000x3000bb.jpg"
    )
    assert (
        assets.video_url
        == "https://mvod.itunes.apple.com/itunes-assets/HLSVideo221/v4/41/85/ad/"
        "4185ad71-e897-fe37-6193-a7dc7abb13f0/P837475808_Anull_video_gr698_sdr_2160x2160-.mp4"
    )


def test_fetch_artwork_assets_without_video() -> None:
    page_url = "https://music.apple.com/album/example-without-video"
    json_payload = load_fixture("test-json-no-video-only-used-data.json")
    html = f"<html><body><div id='serialized-server-data'>{json_payload}</div></body></html>"

    def handler(request: httpx.Request) -> httpx.Response:  # type: ignore[override]
        if request.url == httpx.URL(page_url):
            return httpx.Response(200, text=html, headers={"Content-Type": "text/html"})
        raise AssertionError(f"Unhandled request: {request.url}")

    transport = httpx.MockTransport(handler)
    assets: ArtworkAssets = fetch_artwork_assets(page_url, transport=transport)

    assert assets.image_url == (
        "https://is1-ssl.mzstatic.com/image/thumb/Music211/v4/c5/9a/d0/"
        "c59ad049-d5a4-8df2-8564-238472cf497a/24UMGIM28458.rgb.jpg/3000x3000bb.jpg"
    )
    assert assets.video_url is None
