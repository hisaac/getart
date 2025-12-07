# getart

A small Python CLI that extracts the highest quality album art and motion artwork from Apple Music pages.

## Prerequisites

1. [Install `mise`](https://mise.jdx.dev/installing-mise.html).
2. From the project root, run `mise install` to provision `uv` and a Python 3.11 runtime managed by `uv`.

`uv run` automatically creates an isolated environment the first time it executes, so no additional setup is required.

## Usage

```shell
# Run via mise task
$ mise run <apple-music-url>

# Or call the CLI module directly with uv (make sure the src/ directory is on PYTHONPATH)
$ PYTHONPATH=src uv run python -m getart.cli <apple-music-url> [--no-open] [--timeout <seconds>]

# Optional: install a console script into uv's tool cache
$ uv tool install --from . getart
$ getart <apple-music-url>
```

The command prints any discovered artwork URLs and, by default, opens them in your default browser/player. Use `--no-open` to skip launching the assets, or change the network timeout with `--timeout`.

## Development

- Format / lint: handled by your editor or additional tools of choice.
- Tests: `mise test` (runs `uv run pytest`)
- Build distributions: `mise build` (runs `uv build`)
- Cleanup: `mise clean`

The core logic lives under `src/getart/`, and tests with reusable fixtures live under `tests/`.
