from __future__ import annotations

import tempfile
from pathlib import Path
from unittest import mock

import httpx

from getart.cli import main


def test_cli_download_behavior() -> None:
    """Test that CLI downloads files by default."""
    page_url = "https://music.apple.com/album/test-album"
    image_url = "https://example.com/image.jpg"
    test_content = b"test image content"
    
    json_payload = """[{
        "data": {
            "sections": [{
                "containerArtwork": {
                    "dictionary": {
                        "width": 3000,
                        "height": 3000,
                        "url": "https://example.com/image.jpg"
                    }
                },
                "items": [{
                    "title": "Test Album",
                    "subtitleLinks": [{"title": "Test Artist"}]
                }]
            }]
        }
    }]"""
    
    html = f"<html><body><div id='serialized-server-data'>{json_payload}</div></body></html>"
    
    def handler(request: httpx.Request) -> httpx.Response:  # type: ignore[override]
        if request.url == httpx.URL(page_url):
            return httpx.Response(200, text=html, headers={"Content-Type": "text/html"})
        elif request.url == httpx.URL(image_url):
            return httpx.Response(200, content=test_content)
        raise AssertionError(f"Unhandled request: {request.url}")
    
    transport = httpx.MockTransport(handler)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Monkey-patch httpx.Client to use our transport
        original_client_init = httpx.Client.__init__
        
        def mock_init(self, *args, **kwargs):
            kwargs['transport'] = transport
            original_client_init(self, *args, **kwargs)
        
        httpx.Client.__init__ = mock_init
        try:
            result = main([page_url, "--output-dir", tmpdir])
            assert result == 0
            
            # Check that file was downloaded
            expected_file = Path(tmpdir) / "Test Artist - Test Album.jpg"
            assert expected_file.exists()
            assert expected_file.read_bytes() == test_content
        finally:
            httpx.Client.__init__ = original_client_init


def test_cli_no_download_behavior() -> None:
    """Test that CLI only prints URLs with --no-download."""
    page_url = "https://music.apple.com/album/test-album"
    
    json_payload = """[{
        "data": {
            "sections": [{
                "containerArtwork": {
                    "dictionary": {
                        "width": 3000,
                        "height": 3000,
                        "url": "https://example.com/image.jpg"
                    }
                },
                "items": [{
                    "title": "Test Album",
                    "subtitleLinks": [{"title": "Test Artist"}]
                }]
            }]
        }
    }]"""
    
    html = f"<html><body><div id='serialized-server-data'>{json_payload}</div></body></html>"
    
    def handler(request: httpx.Request) -> httpx.Response:  # type: ignore[override]
        if request.url == httpx.URL(page_url):
            return httpx.Response(200, text=html, headers={"Content-Type": "text/html"})
        raise AssertionError(f"Unhandled request: {request.url}")
    
    transport = httpx.MockTransport(handler)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        original_client_init = httpx.Client.__init__
        
        def mock_init(self, *args, **kwargs):
            kwargs['transport'] = transport
            original_client_init(self, *args, **kwargs)
        
        httpx.Client.__init__ = mock_init
        try:
            result = main([page_url, "--no-download"])
            assert result == 0
            
            # Check that no files were created
            files = list(Path(tmpdir).glob("*"))
            assert len(files) == 0
        finally:
            httpx.Client.__init__ = original_client_init
