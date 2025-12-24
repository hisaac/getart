# getart

A small Python CLI that extracts and downloads the highest quality album art and motion artwork from Apple Music pages.

## Prerequisites

1. [Install `mise`](https://mise.jdx.dev/installing-mise.html).
2. From the project root, run `mise install` to provision `uv` and a Python 3.14 runtime (or later) managed by `uv`.

`uv run` automatically creates an isolated environment the first time it executes, so no additional setup is required.

## Usage

```shell
# Run via mise task
$ mise run <apple-music-url>

# Or call the CLI module directly with uv (make sure the src/ directory is on PYTHONPATH)
$ PYTHONPATH=src uv run python -m getart.cli <apple-music-url> [options]

# Optional: install a console script into uv's tool cache
$ uv tool install --from . getart
$ getart <apple-music-url> [options]
```

By default, the command **downloads** discovered artwork to the current directory with filenames formatted as `<artist_name> - <album_name>.<extension>` (e.g., `Willie Nelson - The Border.jpg`). The command prints the URLs of any discovered artwork.

### Options

- `--output-dir <path>` - Specify a directory to save downloaded files (default: current directory)
- `--no-download` - Only print URLs without downloading files
- `--open` - Open downloaded files in your default browser/player after downloading
- `--timeout <seconds>` - Network timeout in seconds (default: 10)

### Examples

```shell
# Download artwork to the current directory
$ getart https://music.apple.com/us/album/the-border/1837337842

# Download to a specific directory
$ getart https://music.apple.com/us/album/the-border/1837337842 --output-dir ~/Music/Artwork

# Only print URLs without downloading
$ getart https://music.apple.com/us/album/the-border/1837337842 --no-download

# Download and open files
$ getart https://music.apple.com/us/album/the-border/1837337842 --open
```

## Development

- Format / lint: handled by your editor or additional tools of choice.
- Tests: `mise test` (runs `uv run pytest`)
- Build distributions: `mise build` (runs `uv build`)
- Cleanup: `mise clean`

The core logic lives under `src/getart/`, and tests with reusable fixtures live under `tests/`.
