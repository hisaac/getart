from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Optional
from urllib.parse import urljoin

import httpx
from httpx import BaseTransport, HTTPError
from bs4 import BeautifulSoup


DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
    )
}


class GetArtError(Exception):
    """Base error for getart failures."""


class InvalidURLError(GetArtError):
    """Raised when the provided URL is invalid."""


class ServerDataNotFoundError(GetArtError):
    """Raised when the serialized server data element cannot be located."""


@dataclass
class ArtworkAssets:
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    artist_name: Optional[str] = None
    album_name: Optional[str] = None


@dataclass
class ServerData:
    json_object: Any

    @classmethod
    def from_json(cls, json_text: str) -> "ServerData":
        return cls(json.loads(json_text))

    def _iter_sections(self) -> Iterable[dict[str, Any]]:
        if not isinstance(self.json_object, list):
            return []
        for entry in self.json_object:
            if not isinstance(entry, dict):
                continue
            data = entry.get("data")
            if not isinstance(data, dict):
                continue
            sections = data.get("sections")
            if not isinstance(sections, list):
                continue
            for section in sections:
                if isinstance(section, dict):
                    yield section

    def image_artwork_url(self) -> Optional[str]:
        for section in self._iter_sections():
            container_art = section.get("containerArtwork")
            if not isinstance(container_art, dict):
                continue
            dictionary = container_art.get("dictionary")
            if not isinstance(dictionary, dict):
                continue
            width = dictionary.get("width")
            height = dictionary.get("height")
            url_template = dictionary.get("url")
            if not all(isinstance(value, int) for value in (width, height)):
                continue
            if not isinstance(url_template, str):
                continue
            return (
                url_template.replace("{w}", str(width))
                .replace("{h}", str(height))
                .replace("{f}", "jpg")
            )
        return None

    def video_playlist_url(self) -> Optional[str]:
        for section in self._iter_sections():
            items = section.get("items")
            if not isinstance(items, list):
                continue
            for item in items:
                if not isinstance(item, dict):
                    continue
                video_artwork = item.get("videoArtwork")
                if not isinstance(video_artwork, dict):
                    continue
                dictionary = video_artwork.get("dictionary")
                if not isinstance(dictionary, dict):
                    continue
                motion_detail = dictionary.get("motionDetailSquare") or dictionary.get(
                    "motionDetail"
                )
                if not isinstance(motion_detail, dict):
                    continue
                video = motion_detail.get("video")
                if isinstance(video, str):
                    return video
        return None

    def artist_name(self) -> Optional[str]:
        for section in self._iter_sections():
            items = section.get("items")
            if not isinstance(items, list):
                continue
            for item in items:
                if not isinstance(item, dict):
                    continue
                subtitle_links = item.get("subtitleLinks")
                if not isinstance(subtitle_links, list) or not subtitle_links:
                    continue
                first_link = subtitle_links[0]
                if not isinstance(first_link, dict):
                    continue
                title = first_link.get("title")
                if isinstance(title, str):
                    return title
        return None

    def album_name(self) -> Optional[str]:
        for section in self._iter_sections():
            items = section.get("items")
            if not isinstance(items, list):
                continue
            for item in items:
                if not isinstance(item, dict):
                    continue
                title = item.get("title")
                if isinstance(title, str):
                    return title
        return None


class AppleMusicClient:
    def __init__(
        self, *, timeout: float = 10.0, transport: BaseTransport | None = None
    ) -> None:
        self._client = httpx.Client(
            timeout=timeout,
            headers=DEFAULT_HEADERS,
            follow_redirects=True,
            transport=transport,
        )

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "AppleMusicClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def fetch_server_data(self, page_url: str) -> ServerData:
        try:
            response = self._client.get(page_url)
            response.raise_for_status()
        except HTTPError as exc:  # pragma: no cover - thin wrapper over httpx
            raise GetArtError(f"Failed to fetch Apple Music page: {exc}") from exc
        html = response.text
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find(id="serialized-server-data")
        if element is None:
            raise ServerDataNotFoundError(
                "serialized-server-data element not present in HTML."
            )
        json_text = element.string or element.text
        if not json_text:
            raise ServerDataNotFoundError(
                "serialized-server-data element contained no JSON."
            )
        return ServerData.from_json(json_text)

    def resolve_video_url(self, playlist_url: str) -> Optional[str]:
        visited: set[str] = set()
        queue: list[str] = [playlist_url]
        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)
            try:
                response = self._client.get(current)
                response.raise_for_status()
            except HTTPError as exc:  # pragma: no cover - thin wrapper over httpx
                raise GetArtError(f"Failed to fetch playlist data: {exc}") from exc
            text = response.text
            mp4_url = _extract_mp4_url(text, current)
            if mp4_url:
                return mp4_url
            for candidate in _extract_playlist_urls(text, current):
                if candidate not in visited:
                    queue.append(candidate)
        return None


def fetch_artwork_assets(
    page_url: str, *, timeout: float = 10.0, transport: BaseTransport | None = None
) -> ArtworkAssets:
    with AppleMusicClient(timeout=timeout, transport=transport) as client:
        server_data = client.fetch_server_data(page_url)
        image_url = server_data.image_artwork_url()
        video_url = None
        playlist_url = server_data.video_playlist_url()
        if playlist_url:
            video_url = client.resolve_video_url(playlist_url)
        artist_name = server_data.artist_name()
        album_name = server_data.album_name()
        return ArtworkAssets(
            image_url=image_url,
            video_url=video_url,
            artist_name=artist_name,
            album_name=album_name,
        )


def _extract_mp4_url(manifest: str, base_url: str) -> Optional[str]:
    url_match = re.search(r"https?://[^\s\"']+\.mp4", manifest)
    if url_match:
        return url_match.group(0)

    uri_match = re.search(r'URI="([^"]+\.mp4)"', manifest)
    if uri_match:
        return urljoin(base_url, uri_match.group(1))

    for line in manifest.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.endswith(".mp4"):
            return urljoin(base_url, line)
    return None


def _extract_playlist_urls(manifest: str, base_url: str) -> Iterable[str]:
    for line in manifest.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.endswith(".m3u8"):
            yield urljoin(base_url, line)


def _sanitize_filename(name: str) -> str:
    """Sanitize a string to be used as a filename."""
    # Replace invalid filename characters with underscores
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        name = name.replace(char, "_")
    # Remove leading/trailing whitespace and dots
    name = name.strip().strip(".")
    return name


def _get_extension_from_url(url: str) -> str:
    """Extract file extension from URL."""
    if url.endswith(".mp4"):
        return "mp4"
    elif url.endswith(".jpg") or ".jpg/" in url:
        return "jpg"
    return "bin"


def generate_filename(
    artist_name: Optional[str],
    album_name: Optional[str],
    asset_type: str,
    extension: str,
) -> str:
    """Generate a filename for downloaded artwork.
    
    Args:
        artist_name: The artist name (if available)
        album_name: The album name (if available)
        asset_type: Type of asset (e.g., 'image', 'video')
        extension: File extension (e.g., 'jpg', 'mp4')
    
    Returns:
        A sanitized filename
    """
    if artist_name and album_name:
        base = f"{_sanitize_filename(artist_name)} - {_sanitize_filename(album_name)}"
    elif album_name:
        base = _sanitize_filename(album_name)
    elif artist_name:
        base = _sanitize_filename(artist_name)
    else:
        base = f"artwork_{asset_type}"
    
    # Add suffix for video to distinguish from image
    if asset_type == "video":
        return f"{base}_video.{extension}"
    return f"{base}.{extension}"


def download_file(
    url: str,
    output_path: Path,
    *,
    timeout: float = 30.0,
    chunk_size: int = 8192,
) -> None:
    """Download a file from a URL to the specified path.
    
    Args:
        url: The URL to download from
        output_path: The path where the file should be saved
        timeout: Network timeout in seconds
        chunk_size: Size of chunks to read/write
    
    Raises:
        GetArtError: If download fails
    """
    try:
        with httpx.Client(timeout=timeout, follow_redirects=True) as client:
            with client.stream("GET", url) as response:
                response.raise_for_status()
                with open(output_path, "wb") as f:
                    for chunk in response.iter_bytes(chunk_size=chunk_size):
                        f.write(chunk)
    except HTTPError as exc:
        raise GetArtError(f"Failed to download file from {url}: {exc}") from exc
    except OSError as exc:
        raise GetArtError(f"Failed to write file to {output_path}: {exc}") from exc
