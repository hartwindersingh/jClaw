# Developer: Hartwinder Singh
# Copyright (c) 2026 Hartwinder Singh
import shutil
import subprocess
import pytest
from jclaw_app.core.git_ops import status

@pytest.mark.skipif(shutil.which("git") is None, reason="Git not installed")
def test_git_status(tmp_path):
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    (tmp_path / "a.txt").write_text("hello", encoding="utf-8")
    assert "a.txt" in status(tmp_path)
