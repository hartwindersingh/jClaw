from pathlib import Path
import subprocess

def _git(root: str | Path, *args: str, timeout: int = 20) -> str:
    proc = subprocess.run(["git", *args], cwd=str(root), capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=timeout)
    if proc.returncode:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip() or "Git command failed")
    return proc.stdout

def git_available() -> bool:
    try:
        subprocess.run(["git", "--version"], capture_output=True, check=True, timeout=5)
        return True
    except Exception:
        return False

def status(root: str | Path) -> str:
    return _git(root, "status", "--short", "--branch")

def diff(root: str | Path, max_chars: int = 30000) -> str:
    result = _git(root, "diff", "--", timeout=30)
    if not result.strip():
        result = _git(root, "diff", "--cached", "--", timeout=30)
    return result[:max_chars] + ("\n[diff truncated]" if len(result) > max_chars else "")
