from __future__ import annotations

import tempfile
from pathlib import Path

import httpx
import pytest

from getart.core import GetArtError, download_file, generate_filename


def test_generate_filename_with_artist_and_album() -> None:
    filename = generate_filename("Willie Nelson", "The Border", "image", "jpg")
    assert filename == "Willie Nelson - The Border.jpg"


def test_generate_filename_with_artist_only() -> None:
    filename = generate_filename("Willie Nelson", None, "image", "jpg")
    assert filename == "Willie Nelson.jpg"


def test_generate_filename_with_album_only() -> None:
    filename = generate_filename(None, "The Border", "image", "jpg")
    assert filename == "The Border.jpg"


def test_generate_filename_without_metadata() -> None:
    filename = generate_filename(None, None, "image", "jpg")
    assert filename == "artwork_image.jpg"


def test_generate_filename_video() -> None:
    filename = generate_filename("Willie Nelson", "The Border", "video", "mp4")
    assert filename == "Willie Nelson - The Border_video.mp4"


def test_generate_filename_sanitizes_invalid_chars() -> None:
    filename = generate_filename('Artist/Name', 'Album:Title"Test', "image", "jpg")
    assert filename == "Artist_Name - Album_Title_Test.jpg"


def test_download_file_success() -> None:
    test_content = b"test image content"
    test_url = "https://example.com/image.jpg"

    def handler(request: httpx.Request) -> httpx.Response:  # type: ignore[override]
        if request.url == httpx.URL(test_url):
            return httpx.Response(200, content=test_content)
        raise AssertionError(f"Unhandled request: {request.url}")

    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "test_image.jpg"
        transport = httpx.MockTransport(handler)
        
        # Monkey-patch httpx.Client to use our transport
        original_client_init = httpx.Client.__init__
        
        def mock_init(self, *args, **kwargs):
            kwargs['transport'] = transport
            original_client_init(self, *args, **kwargs)
        
        httpx.Client.__init__ = mock_init
        try:
            download_file(test_url, output_path)
            assert output_path.exists()
            assert output_path.read_bytes() == test_content
        finally:
            httpx.Client.__init__ = original_client_init


def test_download_file_http_error() -> None:
    test_url = "https://example.com/notfound.jpg"

    def handler(request: httpx.Request) -> httpx.Response:  # type: ignore[override]
        return httpx.Response(404)

    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "test_image.jpg"
        transport = httpx.MockTransport(handler)
        
        original_client_init = httpx.Client.__init__
        
        def mock_init(self, *args, **kwargs):
            kwargs['transport'] = transport
            original_client_init(self, *args, **kwargs)
        
        httpx.Client.__init__ = mock_init
        try:
            with pytest.raises(GetArtError, match="Failed to download file"):
                download_file(test_url, output_path)
        finally:
            httpx.Client.__init__ = original_client_init
