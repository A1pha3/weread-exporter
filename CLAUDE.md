# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python tool for exporting WeRead (微信读书) books to multiple e-book formats (EPUB, PDF, MOBI, TXT, Markdown). It uses Canvas Hook technology to bypass content protection and extract original rendered content from the WeRead web platform.

## Core Architecture

The project follows a modular architecture with four main layers:

1. **CLI Layer** (`__main__.py`): Command-line interface, argument parsing, and configuration
2. **Business Layer** (`export.py`): Export workflow control, chapter management, and format conversion
3. **Browser Layer** (`webpage.py`): Browser automation, Canvas Hook injection, and content interception
4. **Utility Layer** (`utils.py`): Helper functions for HTTP requests, book lists, and ID management

## Key Components

- **WeReadWebPage**: Manages browser instances and page navigation using pyppeteer
- **WeReadExporter**: Handles the export process and format conversions
- **Canvas Hook**: JavaScript injection to intercept Canvas rendering operations (see `hook.js`)
- **Multi-format support**: EPUB (ebooklib), PDF (weasyprint), MOBI (requires Linux), TXT, Markdown

## Common Development Commands

```bash
# Install the package in development mode
pip install -e .

# Run the CLI tool
weread-exporter -b <book-id> -o epub -o pdf

# Run with specific options
weread-exporter -b <book-id> --headless --load-timeout 120

# Export from a book list (auto-fetches book IDs)
weread-exporter -b <booklist-id>

# List book IDs from a book list
weread-exporter -b <booklist-id> --list-ids

# List available book lists for current user
weread-exporter --list-booklists

# Run tests (uses custom test runner)
python scripts/test_runner.py

# Build the package
python setup.py sdist bdist_wheel

# Build executable (requires pyinstaller)
python scripts/build.py
```

## Code Quality Commands

```bash
# Format code with black
black weread_exporter/

# Lint with flake8
flake8 weread_exporter/

# Type checking with mypy
mypy weread_exporter/
```

## Development Setup

1. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   # Or with dev dependencies:
   pip install -e ".[dev]"
   ```

3. The project uses:
   - pyppeteer for browser automation
   - beautifulsoup4 for HTML parsing
   - ebooklib for EPUB generation
   - weasyprint for PDF rendering (pinned to 52.5)
   - aiohttp for async HTTP requests

## Important Implementation Details

### Canvas Hook Technology
The core technology uses JavaScript Proxy objects to intercept Canvas drawing operations in the browser, allowing extraction of text content even when the original source is protected. The hook script is embedded in `webpage.py` and injected at runtime.

### Async Architecture
The entire system is built on asyncio for high-performance concurrent operations, especially when processing multiple chapters or books. The CLI entry point creates its own event loop in `main()`.

### Platform Patches
- **Windows**: DLL patches for Chrome are applied via `patch_windows()` in `__main__.py`
- **pyppeteer**: `patch_generateRequestHash()` removes Origin header to bypass CORS issues

### Cache System
- Cookies are stored in `cache/cookie.txt`
- Book metadata is cached in `cache/<book-id>/meta.json`
- Chapters are saved as Markdown files in `cache/<book-id>/chapters/`
- Images are downloaded to `cache/<book-id>/images/`

### Browser Anti-detection
The tool implements several anti-detection mechanisms in `webpage.py`:
- Removes webdriver navigator property
- Sets realistic user agent (optional via `--mock-user-agent`)
- Handles request headers properly
- Supports proxy configuration via `--proxy-server`

## Book ID Format

- Single book: Direct 32-character ID (e.g., `08232ac0720befa90825d88`)
- Book list: Contains underscore separator (e.g., `12345_67890`)
  - When a book list ID is detected, the tool automatically fetches all book IDs from the list

## Output Structure

```
output/
├── <book-title>.epub
├── <book-title>.pdf
├── <book-title>.mobi  (Linux only)
└── <book-title>.txt
```

## Error Handling

The tool includes retry mechanisms for:
- Network errors (exponential backoff via load interval)
- Browser crashes (automatic restart in the export loop)
- Chapter loading failures (`LoadChapterFailedError` triggers retry with new browser)

## Platform-specific Notes

- **Windows**: Uses PNG format for PDF images, includes DLL patches for Chrome
- **Linux**: Required for MOBI conversion (uses `ebook-convert` command)
- **macOS**: Full support for all features

## Security Considerations

The tool is designed for personal use only and includes:
- No data collection or transmission
- Local-only processing
- Respect for rate limits (configurable via `--load-interval`)
- Compliance with terms of service