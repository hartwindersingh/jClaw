# Developer: Hartwinder Singh
# Copyright (c) 2026 Hartwinder Singh
from jclaw_app.core.scanner import scan_project

def test_scan_counts_files(tmp_path):
    (tmp_path / "hello.py").write_text("def hi():\n    return 1\n", encoding="utf-8")
    (tmp_path / ".venv").mkdir()
    (tmp_path / ".venv" / "hidden.py").write_text("x=1", encoding="utf-8")
    result = scan_project(tmp_path)
    assert result["file_count"] == 1
    assert result["python_modules"][0]["symbols"][0]["name"] == "hi"
