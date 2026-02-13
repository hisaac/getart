from __future__ import annotations

from pytest import CaptureFixture, MonkeyPatch

from getart.cli import main, normalize_url
from getart.core import ArtworkAssets


def test_normalize_url_beta_domain() -> None:
    url = "https://beta.music.apple.com/us/album/infinite/1837337842"
    assert normalize_url(url) == "https://music.apple.com/us/album/infinite/1837337842"


def test_normalize_url_regular_domain() -> None:
    url = "https://music.apple.com/us/album/infinite/1837337842"
    assert normalize_url(url) == url


def test_main_print_only_does_not_open_assets(
    monkeypatch: MonkeyPatch, capsys: CaptureFixture[str]
) -> None:
    opened_urls: list[str] = []

    def fake_fetch_artwork_assets(_url: str) -> ArtworkAssets:
        return ArtworkAssets(
            image_url="https://example.com/image.jpg",
            video_url="https://example.com/video.mp4",
        )

    def fake_open_asset(url: str) -> None:
        opened_urls.append(url)

    monkeypatch.setattr("getart.cli.fetch_artwork_assets", fake_fetch_artwork_assets)
    monkeypatch.setattr("getart.cli._open_asset", fake_open_asset)

    exit_code = main(
        ["--print-only", "https://music.apple.com/us/album/infinite/1837337842"]
    )
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "image_url URL: https://example.com/image.jpg" in captured.out
    assert "video_url URL: https://example.com/video.mp4" in captured.out
    assert opened_urls == []


def test_main_no_args_prints_help(capsys: CaptureFixture[str]) -> None:
    exit_code = main([])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Fetch high-quality Apple Music artwork and motion assets." in captured.out
    assert "--print-only" in captured.out
    assert captured.err == ""
