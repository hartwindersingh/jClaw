# Changelog

## 0.2.0 — 2026-11-15
- Added an OpenClaw Gateway tab with Gateway status diagnostics.
- Added agent delegation through the official `openclaw agent` CLI, which routes requests through the configured Gateway by default.
- Added configurable agent ID and persistent session key.
- Added project inventory context to engineering requests with clear limits on source access.
- Moved OpenClaw and Ollama inference calls to background threads to keep the GUI responsive.
- Kept local Ollama available as a separate backend.
- Added tests for the OpenClaw CLI bridge.
- Updated About window, package metadata and installation documentation.

Developer: Hartwinder Singh
Copyright (c) 2026 Hartwinder Singh
