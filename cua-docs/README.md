# CUA Documentation Mirror

This folder contains a complete offline mirror of the CUA (Computer Use Agent) documentation from https://www.cua.ai/docs.

## Mirror Details

- **Source URL**: https://www.cua.ai/docs
- **Mirror Date**: October 12, 2025
- **Files Downloaded**: 97 files
- **Total Size**: 15MB
- **Tool Used**: wget --mirror with link conversion

## What's Included

- Complete HTML documentation with full formatting
- All CSS stylesheets and JavaScript files
- Images, fonts, and other assets
- Responsive design and theme switching
- Navigation sidebar and search functionality
- All internal links converted for offline viewing

## How to View

1. Open `www.cua.ai/docs/index.html` in your web browser
2. Alternatively, serve the files with a local web server:
   ```bash
   cd cua-docs/www.cua.ai/docs
   python -m http.server 8000
   ```
   Then visit http://localhost:8000

## Content Overview

The documentation covers:

- **Quickstart Guides**: Getting started with CUA for developers and CLI users
- **Agent SDK**: Building and customizing computer use agents
- **Computer SDK**: Computer control and automation
- **Libraries**: Core libraries (Agent, Computer, Lume, Lumier, MCP Server, etc.)
- **API Reference**: Complete API documentation
- **Benchmarks**: Performance testing and evaluation
- **Telemetry**: Usage tracking and analytics

## Technical Notes

- All links have been converted from absolute to relative paths for offline functionality
- The site uses a modern documentation framework with dark/light theme support
- JavaScript is included for interactive features like search and navigation
- Fonts and icons are embedded locally

## Mirror Creation Command

```bash
wget --mirror \
     --convert-links \
     --adjust-extension \
     --page-requisites \
     --no-parent \
     --execute robots=off \
     --wait=1 \
     --random-wait \
     --no-check-certificate \
     --user-agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36" \
     -P cua-docs \
     https://www.cua.ai/docs
```

This ensures complete offline access to CUA documentation with identical appearance and functionality to the live site.