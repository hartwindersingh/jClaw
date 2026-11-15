# Developer: Hartwinder Singh
# Copyright (c) 2026 Hartwinder Singh
from pathlib import Path
from collections import Counter
import ast

DEFAULT_IGNORES = {".git", ".venv", "venv", "__pycache__", "node_modules", "dist", "build", ".idea", ".pytest_cache", ".mypy_cache", ".ruff_cache"}

def scan_project(project: str | Path, max_files: int = 5000) -> dict:
    root = Path(project).expanduser().resolve()
    if not root.is_dir():
        raise ValueError(f"Not a directory: {root}")
    counts, files, python_modules, large_files = Counter(), [], [], []
    total_bytes = 0
    for path in root.rglob("*"):
        if any(part in DEFAULT_IGNORES for part in path.parts) or not path.is_file():
            continue
        try:
            rel, size = path.relative_to(root).as_posix(), path.stat().st_size
        except OSError:
            continue
        counts[path.suffix.lower() or "[no extension]"] += 1
        total_bytes += size
        if size > 2_000_000:
            large_files.append({"path": rel, "bytes": size})
        if len(files) < max_files:
            files.append({"path": rel, "bytes": size, "extension": path.suffix.lower()})
        if path.suffix.lower() == ".py" and len(python_modules) < 500:
            try:
                tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
                symbols = [{"kind": "class" if isinstance(n, ast.ClassDef) else "function", "name": n.name, "line": n.lineno}
                           for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))]
                python_modules.append({"path": rel, "symbols": symbols[:200]})
            except (OSError, SyntaxError, ValueError):
                python_modules.append({"path": rel, "symbols": [], "parse_error": True})
    return {"root": str(root), "file_count": sum(counts.values()), "listed_files": len(files),
            "total_bytes": total_bytes, "extensions": dict(counts.most_common()),
            "large_files": large_files[:100], "files": files, "python_modules": python_modules,
            "truncated": sum(counts.values()) > max_files}

def format_summary(report: dict) -> str:
    lines = [f"Project: {report['root']}", f"Files: {report['file_count']} (listed {report['listed_files']})",
             f"Total size: {report['total_bytes']:,} bytes",
             "Extensions: " + ", ".join(f"{k}: {v}" for k, v in report["extensions"].items()), "",
             "Python modules and symbols:"]
    for module in report["python_modules"][:100]:
        names = ", ".join(f"{s['kind']} {s['name']} (L{s['line']})" for s in module["symbols"][:30])
        lines.append(f"- {module['path']}: {names or '(no symbols found)'}")
    if report["truncated"]:
        lines.append("[File listing truncated at configured limit]")
    return "\n".join(lines)
