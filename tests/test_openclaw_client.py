# Developer: Hartwinder Singh
# Copyright (c) 2026 Hartwinder Singh
import json
from unittest.mock import patch
import pytest
from jclaw_app.core import openclaw_client as oc

def test_find_cli_missing(monkeypatch):
    monkeypatch.setattr(oc.shutil, "which", lambda _name: None)
    with pytest.raises(oc.OpenClawError):
        oc.find_cli()

def test_ask_agent_builds_gateway_command(monkeypatch):
    calls = {}
    def fake_run(args, **kwargs):
        calls["args"] = args
        return type("Result", (), {"returncode": 0, "stdout": json.dumps({"result":{"text":"done"}}), "stderr": ""})()
    monkeypatch.setattr(oc, "find_cli", lambda _p=None: "openclaw")
    monkeypatch.setattr(oc.subprocess, "run", fake_run)
    answer = oc.ask_agent("Review this", agent_id="dev", session_key="agent:dev:jclaw")
    assert answer == "done"
    assert calls["args"][:4] == ["openclaw", "agent", "--agent", "dev"]
    assert "--local" not in calls["args"]

def test_rejects_empty_prompt():
    with pytest.raises(ValueError):
        oc.ask_agent("  ")
