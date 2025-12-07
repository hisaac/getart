from __future__ import annotations

import argparse
import sys
import webbrowser
from dataclasses import asdict
from typing import Sequence
from urllib.parse import urlparse

from .core import (
    ArtworkAssets,
    GetArtError,
    InvalidURLError,
    fetch_artwork_assets,
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
        "--no-open",
        action="store_true",
        help="Do not open discovered assets in the default browser.",
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
        assets: ArtworkAssets = fetch_artwork_assets(normalized_url, timeout=args.timeout)
    except GetArtError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except Exception as exc:  # pragma: no cover - defensive fallback
        print(f"Unexpected error: {exc}", file=sys.stderr)
        return 2

    output = {key: value for key, value in asdict(assets).items() if value is not None}
    if not output:
        print("No artwork assets were discovered.")
        return 0

    for label, asset_url in output.items():
        print(f"{label} URL: {asset_url}")
        if not args.no_open:
            _open_asset(asset_url)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
