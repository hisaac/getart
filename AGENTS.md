# AGENTS.md

This file is guidance for coding agents working in `getart`.

## Project snapshot

- Language: Python (`>=3.14`)
- Package layout: `src/getart/`
- Entry point: `getart.cli:main`
- Core logic: `src/getart/core.py`
- Tests: `tests/` (pytest, fixture-heavy, network mocked)
- Tooling/runtime: `mise` + `uv`

## First commands to run

From repo root:

```sh
mise install
mise run bootstrap
mise run test
```

If you only need tests:

```sh
mise run test
```

## Daily command reference

- Run CLI with mise task:
  - `mise run run "<apple-music-url>"`
- Run CLI module directly:
  - `PYTHONPATH=src uv run python -m getart.cli "<apple-music-url>"`
- Run checks:
  - `mise run check`
- Run tests:
  - `mise run test`
- Build:
  - `mise run build`

## Code boundaries and responsibilities

- Keep URL parsing and CLI behavior in `src/getart/cli.py`.
- Keep Apple Music fetching/parsing logic in `src/getart/core.py`.
- Reuse existing error types (`GetArtError` and subclasses) before creating new ones.
- Prefer pure helpers for parsing (`_extract_mp4_url`, `_extract_playlist_urls`) and unit test them via public flows.

## Testing expectations

- Do not rely on live Apple Music/network in tests.
- Use `httpx.MockTransport` for request/response control.
- Reuse fixtures in `tests/data/` where possible; add new minimal fixtures when needed.
- For behavior changes in parsing or fetch flow, add/update tests in:
  - `tests/test_core.py`
  - `tests/test_server_data.py`
  - `tests/test_cli.py`

## Style and formatting notes

- Follow `.editorconfig`:
  - Python: spaces, size 4
  - YAML: spaces, size 2
  - Shell/common defaults: tabs unless overridden
- Keep changes small and direct; avoid broad refactors unless requested.
- Preserve current type-hint style and dataclass usage.

## Shell/script notes

- Shared shell helpers live in `scripts/lib/common.bash`; source this from project scripts.
- `scripts/update-hk-import` rewrites header lines in `hk.pkl` based on installed `hk` version.
- CI runs:
  - `mise run check`
  - `mise run test`
  Keep both green before finishing.

## Agent workflow recommendation

1. Read `README.md`, target module(s), and related tests first.
2. Implement minimal change in `src/getart/`.
3. Add or adjust tests near affected behavior.
4. Run `mise run test` (and `mise run check` when relevant).
5. Summarize changed files and any residual risks.

## Do and Don't

Do:

- Do keep behavior changes covered by tests in `tests/`.
- Do preserve existing CLI exit-code conventions (`0`, `1`, `2`).
- Do prefer explicit, typed data flow with dataclasses and narrow helpers.
- Do keep parsing logic resilient to missing/partial JSON fields.

Don't:

- Don't introduce live network calls in tests.
- Don't add dependencies unless there is a clear, project-level need.
- Don't mix unrelated refactors into behavior fixes.
- Don't swallow actionable errors; return/raise meaningful messages.
