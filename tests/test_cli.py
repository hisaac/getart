from __future__ import annotations

from getart.cli import normalize_url


def test_normalize_url_beta_domain() -> None:
    url = "https://beta.music.apple.com/us/album/infinite/1837337842"
    assert normalize_url(url) == "https://music.apple.com/us/album/infinite/1837337842"


def test_normalize_url_regular_domain() -> None:
    url = "https://music.apple.com/us/album/infinite/1837337842"
    assert normalize_url(url) == url
