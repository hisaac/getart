from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[2]
URL_WITH_VIDEO = "https://music.apple.com/us/album/the-border/1734857782"
URL_WITHOUT_VIDEO = "https://music.apple.com/us/album/lapse/1736201082"


def _run_cli(url: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    src_path = str(PROJECT_ROOT / "src")
    existing_pythonpath = env.get("PYTHONPATH")
    env["PYTHONPATH"] = (
        src_path
        if not existing_pythonpath
        else f"{src_path}{os.pathsep}{existing_pythonpath}"
    )

    return subprocess.run(
        [sys.executable, "-m", "getart.cli", "--print-only", url],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=60,
        env=env,
        check=False,
    )


@pytest.mark.integration
def test_cli_live_album_outputs_artwork() -> None:
    result = _run_cli(URL_WITH_VIDEO)

    assert result.returncode == 0, (
        f"CLI failed with exit code {result.returncode}\n"
        f"stdout:\n{result.stdout}\n\n"
        f"stderr:\n{result.stderr}"
    )
    assert "image_url URL: https://is1-ssl.mzstatic.com/image/thumb/" in result.stdout
    assert "video_url URL:" in result.stdout


@pytest.mark.integration
def test_cli_live_album_without_video_omits_video_output() -> None:
    result = _run_cli(URL_WITHOUT_VIDEO)

    assert result.returncode == 0, (
        f"CLI failed with exit code {result.returncode}\n"
        f"stdout:\n{result.stdout}\n\n"
        f"stderr:\n{result.stderr}"
    )
    assert "image_url URL: https://is1-ssl.mzstatic.com/image/thumb/" in result.stdout
    assert "video_url URL:" not in result.stdout
