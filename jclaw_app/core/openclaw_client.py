"""Safe OpenClaw CLI bridge. The CLI routes agent turns through the configured Gateway.

Developer: Hartwinder Singh
Copyright (c) 2026 Hartwinder Singh
"""
from __future__ import annotations
import json
import os
import shutil
import subprocess
from pathlib import Path

class OpenClawError(RuntimeError):
    pass

def find_cli(explicit_path: str | None = None) -> str:
    candidate = (explicit_path or "").strip()
    if candidate:
        path = Path(candidate).expanduser()
        if path.is_file():
            return str(path.resolve())
        found = shutil.which(candidate)
        if found:
            return found
        raise OpenClawError(f"OpenClaw executable not found: {candidate}")
    found = shutil.which("openclaw") or shutil.which("openclaw.cmd")
    if found:
        return found
    raise OpenClawError("OpenClaw CLI was not found on PATH. Install OpenClaw and reopen jClaw.")

def _run(args: list[str], executable: str | None = None, cwd: str | Path | None = None,
         timeout: int = 30) -> subprocess.CompletedProcess:
    exe = find_cli(executable)
    command = [exe, *args]
    # Windows .cmd launchers require cmd.exe; keep arguments quoted by subprocess list.
    if os.name == "nt" and exe.lower().endswith((".cmd", ".bat")):
        command = ["cmd.exe", "/d", "/s", "/c", subprocess.list2cmdline(command)]
    try:
        result = subprocess.run(command, cwd=str(cwd) if cwd else None, capture_output=True,
                                text=True, encoding="utf-8", errors="replace",
                                timeout=timeout, shell=False)
    except subprocess.TimeoutExpired as exc:
        raise OpenClawError(f"OpenClaw command timed out after {timeout} seconds.") from exc
    except OSError as exc:
        raise OpenClawError(f"Could not start OpenClaw CLI: {exc}") from exc
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        raise OpenClawError(detail or f"OpenClaw exited with code {result.returncode}.")
    return result

def gateway_status(executable: str | None = None, timeout: int = 20) -> str:
    result = _run(["gateway", "status", "--json"], executable=executable, timeout=timeout)
    raw = (result.stdout or result.stderr).strip()
    try:
        data = json.loads(raw)
        return json.dumps(data, indent=2, ensure_ascii=False)
    except json.JSONDecodeError:
        return raw or "OpenClaw Gateway status command completed without output."

def ask_agent(message: str, agent_id: str = "main", session_key: str | None = None,
              executable: str | None = None, cwd: str | Path | None = None,
              timeout: int = 600) -> str:
    message = message.strip()
    agent_id = agent_id.strip()
    if not message:
        raise ValueError("Message cannot be empty.")
    if not agent_id:
        raise ValueError("Agent ID cannot be empty.")
    args = ["agent", "--agent", agent_id, "--message", message, "--json", "--timeout", str(timeout)]
    if session_key and session_key.strip():
        args.extend(["--session-key", session_key.strip()])
    result = _run(args, executable=executable, cwd=cwd, timeout=timeout + 30)
    raw = (result.stdout or "").strip()
    if not raw:
        return "OpenClaw completed the turn but returned no text."
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return raw
    if data.get("ok") is False:
        error = data.get("error") or {}
        raise OpenClawError(error.get("message") or "OpenClaw reported an unsuccessful agent turn.")
    # CLI JSON envelopes may wrap the final assistant text in different stable fields.
    candidates = [data.get("text"), data.get("response"), data.get("reply")]
    result_obj = data.get("result")
    if isinstance(result_obj, dict):
        candidates.extend([result_obj.get("text"), result_obj.get("reply"), result_obj.get("content")])
    for value in candidates:
        if isinstance(value, str) and value.strip():
            return value.strip()
    payload = data.get("payload")
    if isinstance(payload, dict):
        for key in ("text", "reply", "content"):
            if isinstance(payload.get(key), str) and payload[key].strip():
                return payload[key].strip()
    return json.dumps(data, indent=2, ensure_ascii=False)
