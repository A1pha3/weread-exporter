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
- **Canvas Hook**: JavaScript injection to intercept Canvas rendering operations
- **Multi-format support**: EPUB (ebooklib), PDF (weasyprint), MOBI (requires Linux), TXT, Markdown

## Common Development Commands

```bash
# Install the package in development mode
pip install -e .

# Run the CLI tool
weread-exporter -b <book-id> -o epub -o pdf

# Run with specific options
weread-exporter -b <book-id> --headless --load-timeout 120

# Export from a book list
weread-exporter -b <booklist-id> --list-ids

# List available book lists
weread-exporter --list-booklists

# Run tests
python -m pytest tests/

# Build the package
python setup.py sdist bdist_wheel
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
   ```

3. The project uses:
   - pyppeteer for browser automation
   - beautifulsoup4 for HTML parsing
   - ebooklib for EPUB generation
   - weasyprint for PDF rendering
   - aiohttp for async HTTP requests

## Important Implementation Details

### Canvas Hook Technology
The core technology uses JavaScript Proxy objects to intercept Canvas drawing operations in the browser, allowing extraction of text content even when the original source is protected.

### Async Architecture
The entire system is built on asyncio for high-performance concurrent operations, especially when processing multiple chapters or books.

### Cache System
- Cookies are stored in `cache/cookie.txt`
- Book metadata is cached in `cache/<book-id>/meta.json`
- Chapters are saved as Markdown files in `cache/<book-id>/chapters/`
- Images are downloaded to `cache/<book-id>/images/`

### Browser Anti-detection
The tool implements several anti-detection mechanisms:
- Removes webdriver navigator property
- Sets realistic user agent
- Handles request headers properly
- Supports proxy configuration

## Book ID Format

- Single book: Direct 32-character ID (e.g., `08232ac0720befa90825d88`)
- Book list: Contains underscore separator (e.g., `12345_67890`)

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
- Network errors (exponential backoff)
- Browser crashes (automatic restart)
- Chapter loading failures (retry with new browser instance)

## Platform-specific Notes

- **Windows**: Uses PNG format for PDF images, includes DLL patches
- **Linux**: Required for MOBI conversion
- **macOS**: Full support for all features

## Security Considerations

The tool is designed for personal use only and includes:
- No data collection or transmission
- Local-only processing
- Respect for rate limits
- Compliance with terms of service