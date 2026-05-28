from __future__ import annotations

import json
import os
from pathlib import Path

IGNORE_DIRS = {".git", "node_modules", ".next", "__pycache__", ".venv", "venv", "dist", "build", ".turbo", ".cache"}
IGNORE_FILES = {".DS_Store", "package-lock.json", "yarn.lock", "pnpm-lock.yaml"}


def _read(path: Path, max_kb: float = 100.0) -> str | None:
    if not path.is_file():
        return None
    if path.stat().st_size / 1024 > max_kb:
        return None
    for enc in ("utf-8", "latin-1"):
        try:
            return path.read_text(encoding=enc)
        except (UnicodeDecodeError, OSError):
            continue
    return None


def _tree(root: Path, prefix: str = "", depth: int = 0, max_depth: int = 4) -> str:
    if depth >= max_depth:
        return ""
    try:
        entries = sorted(root.iterdir(), key=lambda e: (not e.is_dir(), e.name.lower()))
    except PermissionError:
        return ""
    entries = [e for e in entries if not (e.is_dir() and e.name in IGNORE_DIRS) and e.name not in IGNORE_FILES]
    lines = []
    for i, entry in enumerate(entries):
        last = i == len(entries) - 1
        connector = "└── " if last else "├── "
        lines.append(f"{prefix}{connector}{entry.name}{'/' if entry.is_dir() else ''}")
        if entry.is_dir():
            sub = _tree(entry, prefix + ("    " if last else "│   "), depth + 1, max_depth)
            if sub:
                lines.append(sub)
    return "\n".join(lines)


def get_directory_tree(repo_path: Path) -> str:
    return _tree(repo_path)


def get_readme(repo_path: Path) -> str | None:
    for name in ("README.md", "readme.md", "Readme.md", "README"):
        content = _read(repo_path / name, max_kb=50.0)
        if content:
            return content
    return None


def get_package_json(repo_path: Path) -> dict | None:
    content = _read(repo_path / "package.json")
    if content:
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass
    return None


def get_important_files(repo_path: Path) -> dict[str, str | None]:
    names = [
        "app.py","main.py",
        "tsconfig.json", "next.config.js", "next.config.ts", "next.config.mjs",
        "tailwind.config.js", "tailwind.config.ts", ".eslintrc.json", ".eslintrc.js",
        "vite.config.ts", "vite.config.js", "app/layout.tsx", "src/app/layout.tsx",
    ]
    return {n: _read(repo_path / n) for n in names if (repo_path / n).exists()}


def get_file_contents(repo_path: Path, file_paths: list[str]) -> dict[str, str]:
    return {p: c for p in file_paths if (c := _read(repo_path / p)) is not None}
