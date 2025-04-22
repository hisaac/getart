# getart

A small macOS command-line utility for fetching artwork from web pages.

## Overview

This utility fetches HTML content from a provided URL, extracts JSON data from a specific element, and opens image or video artwork in the system's default applications.

## Implementation

This tool uses:
- Swift's JSONSerialization for JSON parsing
- SwiftSoup for HTML parsing
- M3U8Parser for handling video playlists

## Usage

1. [Install `mise`](https://mise.jdx.dev/installing-mise.html)
2. Build and run the tool using `mise`:
	```shell
	$ mise run <url>
	```
