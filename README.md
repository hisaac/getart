# getart

A small Python CLI that extracts the highest quality album art and motion artwork from Apple Music pages.

## Prerequisites

1. [Install `mise`](https://mise.jdx.dev/installing-mise.html).
2. From the project root, run `mise install` to provision `uv` and a Python 3.14 runtime (or later) managed by `uv`.

`uv run` automatically creates an isolated environment the first time it executes, so no additional setup is required.

## Usage

```shell
# Run via mise task
$ mise run <apple-music-url>

# Or call the CLI module directly with uv (make sure the src/ directory is on PYTHONPATH)
$ PYTHONPATH=src uv run python -m getart.cli <apple-music-url>

# Print URLs without opening browser/player
$ PYTHONPATH=src uv run python -m getart.cli --print-only <apple-music-url>

# Optional: install a console script into uv's tool cache
$ uv tool install --from . getart
$ getart <apple-music-url>
```

The command prints any discovered artwork URLs and opens them in your default browser/player.

## Development

- Format / lint: handled by your editor or additional tools of choice.
- Unit tests: `mise run test-unit`
- Live integration tests: `mise run test-integration` (hits real Apple Music URLs)
- Full suite (unit + integration): `mise run test`
- Build distributions: `mise build` (runs `uv build`)
- Cleanup: `mise clean`

The core logic lives under `src/getart/`, and tests with reusable fixtures live under `tests/`.
