# jClaw Engineering Suite

**Developer:** Hartwinder Singh  
**Copyright:** Copyright (c) 2026 Hartwinder Singh  
**Licence:** MIT

jClaw is a local-first software-engineering desktop workspace. It complements OpenClaw rather than replacing it: jClaw provides project inspection, Git review and test workflows, while OpenClaw supplies the configured agent runtime through its Gateway. Ollama remains available as an independent local model option.

## Release
**0.2.0 — OpenClaw Gateway integration preview.** The Gateway bridge uses the official `openclaw agent` CLI entry point, which routes turns through the configured Gateway by default. jClaw does not hand-roll or bypass the Gateway authentication protocol.

## Requirements
- Windows 10 (22H2 recommended) or a supported Python desktop environment
- Python 3.10+
- OpenClaw installed, configured and its Gateway running for Gateway features
- Ollama and a downloaded model only if you want Local Ollama
- Git for Git status/diff features
- Internet is not required for jClaw itself after dependencies and models are installed; OpenClaw's own model/provider setup determines its network needs.

## Install
1. Install Python 3.10 or newer.
2. Install OpenClaw and complete its onboarding: https://docs.openclaw.ai/
3. Confirm the Gateway is running: `openclaw gateway status`.
4. Clone this repository and open PowerShell in the folder:
   ```powershell
   py -m venv .venv
   .venv\Scripts\activate
   py -m pip install -e ".[dev]"
   jclaw
   ```
5. In jClaw, open **OpenClaw Gateway**. Leave CLI path as `openclaw` if it is on PATH. Set the configured agent ID (default `main`), optionally choose a session key, and click **Check Gateway**.
6. Select a project folder, run **Scan Project**, then submit an engineering request from the Gateway tab.

If OpenClaw is installed in a non-standard location, enter the full path to its executable/launcher in the CLI path field.

## OpenClaw integration design
- Uses `openclaw gateway status --json` for a Gateway diagnostic.
- Uses `openclaw agent --agent <id> --message <task> --json` for agent turns. This command uses the Gateway by default; jClaw deliberately does not pass `--local`.
- A persistent session key lets related jClaw requests continue in the same OpenClaw conversation. Change it to start a separate conversation.
- The selected project inventory is passed as context. It is metadata, not a copy of source files; the OpenClaw agent can only inspect or operate on project files if its configured tools and workspace permissions allow access to that path.
- Agent requests run on a background thread so the desktop remains responsive.
- Gateway authentication is handled by the OpenClaw CLI and its existing configuration. Do not paste Gateway tokens into jClaw or put tokens in URLs.
- The configured OpenClaw agent may have tools capable of executing commands or modifying files. Review its tool policy and workspace permissions. jClaw asks it not to make changes without approval, but the agent's own policy is the actual enforcement boundary.

## Local Ollama
Install Ollama: https://ollama.com/download/windows  
Download a small coding model once:
```powershell
ollama pull qwen2.5-coder:3b
```
Open **Local Ollama**, refresh models and select the model. Once dependencies and the model are downloaded, local chat can run without a hosted model API.

## Included features
- Project inventory and Python symbol scan
- Git status and diff preview (read-only)
- Explicit, confirmation-gated pytest execution
- OpenClaw Gateway diagnostics and agent delegation
- Persistent OpenClaw session key setting
- Local Ollama chat as a separate option
- Background execution for agent calls
- Activity log under `~/.jclaw/activity.jsonl`
- About window with developer attribution

## Safety and limitations
- jClaw does not silently edit source files, commit, push, create pull requests or publish releases.
- Test execution can execute arbitrary project code. Run tests only in repositories you trust.
- OpenClaw agents may have broad tools. Configure least-privilege agent policies and workspace sandboxing in OpenClaw itself.
- Project summary metadata is sent to the selected OpenClaw agent with your prompt. Do not include secrets in project names or prompts.
- OpenClaw Gateway availability and agent/provider readiness are controlled by the OpenClaw installation.
- The Gateway bridge is CLI-mediated, not a separately implemented WebSocket client. This keeps authentication, protocol compatibility, pairing and reconnect behavior under the official CLI.
- Windows GUI runtime, installer signing and hardware-specific acceptance need testing on a Windows machine before calling this a fully certified production release.

## Development
```powershell
py -m pip install -e ".[dev]"
pytest
```

## Attribution
All project code and documentation are maintained with **Hartwinder Singh** as developer attribution. New modules should use shared constants from `jclaw_app.metadata`.
