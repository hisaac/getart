from __future__ import annotations

import argparse
import sys
import webbrowser
from dataclasses import asdict
from pathlib import Path
from typing import Sequence
from urllib.parse import urlparse

from .core import (
    ArtworkAssets,
    GetArtError,
    InvalidURLError,
    download_file,
    fetch_artwork_assets,
    generate_filename,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Fetch high-quality Apple Music artwork and motion assets."
    )
    parser.add_argument("url", help="Apple Music URL to inspect.")
    parser.add_argument(
        "--timeout",
        type=float,
        default=10.0,
        help="Network timeout in seconds (default: 10).",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=".",
        help="Directory to save downloaded files (default: current directory).",
    )
    parser.add_argument(
        "--no-download",
        action="store_true",
        help="Do not download files, only print URLs.",
    )
    parser.add_argument(
        "--open",
        action="store_true",
        help="Open downloaded files in the default browser/player.",
    )
    return parser


def validate_url(candidate: str) -> None:
    parsed = urlparse(candidate)
    if not parsed.scheme or not parsed.netloc:
        raise InvalidURLError(f"Invalid URL provided: {candidate!r}")


def normalize_url(candidate: str) -> str:
    parsed = urlparse(candidate)
    if parsed.netloc.startswith("beta.") and len(parsed.netloc) > len("beta."):
        netloc = parsed.netloc[len("beta.") :]
        normalized = parsed._replace(netloc=netloc)
        return normalized.geturl()
    return candidate


def _open_asset(asset_url: str) -> None:
    try:
        webbrowser.open(asset_url)
    except webbrowser.Error:
        # Failing to open the browser shouldn't abort the CLI.
        pass


def _get_extension_from_url(url: str) -> str:
    """Extract file extension from URL."""
    if url.endswith(".mp4"):
        return "mp4"
    elif url.endswith(".jpg") or ".jpg/" in url:
        return "jpg"
    return "bin"


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        validate_url(args.url)
    except InvalidURLError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    normalized_url = normalize_url(args.url)

    try:
        assets: ArtworkAssets = fetch_artwork_assets(
            normalized_url, timeout=args.timeout
        )
    except GetArtError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except Exception as exc:  # pragma: no cover - defensive fallback
        print(f"Unexpected error: {exc}", file=sys.stderr)
        return 2

    # Check if we have any artwork URLs
    if not assets.image_url and not assets.video_url:
        print("No artwork assets were discovered.")
        return 0

    output_dir = Path(args.output_dir)
    
    # If downloading, create output directory if needed
    if not args.no_download:
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            print(f"Failed to create output directory: {exc}", file=sys.stderr)
            return 2

    # Process image URL
    if assets.image_url:
        print(f"image_url: {assets.image_url}")
        if not args.no_download:
            extension = _get_extension_from_url(assets.image_url)
            filename = generate_filename(
                assets.artist_name, assets.album_name, "image", extension
            )
            output_path = output_dir / filename
            try:
                download_file(assets.image_url, output_path, timeout=args.timeout)
                print(f"Downloaded: {output_path}")
                if args.open:
                    _open_asset(str(output_path))
            except GetArtError as exc:
                print(f"Failed to download image: {exc}", file=sys.stderr)

    # Process video URL
    if assets.video_url:
        print(f"video_url: {assets.video_url}")
        if not args.no_download:
            extension = _get_extension_from_url(assets.video_url)
            filename = generate_filename(
                assets.artist_name, assets.album_name, "video", extension
            )
            output_path = output_dir / filename
            try:
                download_file(assets.video_url, output_path, timeout=args.timeout)
                print(f"Downloaded: {output_path}")
                if args.open:
                    _open_asset(str(output_path))
            except GetArtError as exc:
                print(f"Failed to download video: {exc}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
