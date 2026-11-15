# jClaw Engineering Suite

**Developer:** Hartwinder Singh  
**Copyright:** Copyright (c) 2026 Hartwinder Singh  
**Licence:** MIT

A local-first engineering workspace designed to complement OpenClaw. It connects to a local Ollama server and provides repository inspection, Git review, test execution and engineering assistance.

## Release
0.1.0 — prototype / developer preview

## Requirements
- Windows 10 (22H2 recommended)
- Python 3.10+
- Ollama installed locally
- A coding model downloaded in Ollama (for example `qwen2.5-coder:3b`)
- Git is optional; Git features are disabled if Git is unavailable

## Quick start
1. Install Ollama: https://ollama.com/download/windows
2. Download a model once: `ollama pull qwen2.5-coder:3b`
3. Clone this repository.
4. In PowerShell, from the project folder:
   ```powershell
   py -m venv .venv
   .venv\Scripts\activate
   py -m pip install -e .
   jclaw
   ```
   Or run `py -m jclaw_app`.

## Offline operation
After Python dependencies, Ollama and a model are installed, the app communicates with `http://127.0.0.1:11434`. No hosted API key or cloud inference is configured. GitHub publishing and web search are not included in this release.

## Safety
- Project scanning and Git operations are read-only.
- Test execution requires explicit confirmation and can execute project code. Only run tests for projects you trust.
- The assistant suggests changes; it does not silently rewrite project files.
- Do not paste secrets into prompts.

## Included in 0.1.0
- Tkinter desktop interface
- Project file inventory and Python symbol scan
- Git status and diff preview
- Explicit pytest runner
- Local Ollama model discovery and chat
- Basic activity log in the user's home directory
- Help → About jClaw with developer attribution

## Not included yet
- OpenClaw Gateway integration
- Multi-agent orchestration
- Automated file modifications
- GitHub PR/release automation
- Windows executable packaging
- Full forensic/security analysis

## Development
```powershell
py -m pip install -e ".[dev]"
pytest
```

## Attribution
All project code and documentation are maintained with **Hartwinder Singh** as developer attribution. New modules should use constants from `jclaw_app.metadata`.
