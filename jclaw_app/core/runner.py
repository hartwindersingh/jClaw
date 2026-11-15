# Developer: Hartwinder Singh
# Copyright (c) 2026 Hartwinder Singh
from pathlib import Path
import subprocess
import sys

def run_tests(root: str | Path, timeout: int = 300) -> tuple[int, str]:
    root = Path(root).resolve()
    if not (root / "tests").exists() and not list(root.glob("test_*.py")):
        return 0, "No conventional Python tests directory or test_*.py files found. Nothing was run."
    try:
        proc = subprocess.run([sys.executable, "-m", "pytest", "-q"], cwd=root, capture_output=True,
                              text=True, encoding="utf-8", errors="replace", timeout=timeout)
        output = (proc.stdout + "\n" + proc.stderr).strip()
        return proc.returncode, output or f"pytest exited with code {proc.returncode}"
    except FileNotFoundError:
        return 2, "pytest is not installed. Install it with: py -m pip install pytest"
    except subprocess.TimeoutExpired:
        return 124, f"Test run exceeded {timeout} seconds and was stopped."
