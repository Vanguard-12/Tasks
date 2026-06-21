from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any

from agent.tools.git import GitRepo


def run_compileall(root: Path) -> dict[str, Any]:
    fix_common_python_syntax_issues(root)
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "compileall",
            "-q",
            "-x",
            r"(\.git|\.venv|__pycache__|\.agent_reports)",
            ".",
        ],
        cwd=root,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    return {
        "name": "python -m compileall .",
        "ok": result.returncode == 0,
        "output": compact_output(result.stdout + result.stderr),
    }


def run_git_diff_check(repo: GitRepo) -> dict[str, Any]:
    ok, output = repo.diff_check()
    if not ok:
        fix_changed_file_whitespace(repo)
        ok, output = repo.diff_check()
    return {
        "name": "git diff --check",
        "ok": ok,
        "output": compact_output(output),
    }


def run_placeholder_scan(repo: GitRepo) -> dict[str, Any]:
    findings: list[str] = []
    suspicious = (
        "yourusername",
        "your-username",
        "example.com",
        "REPLACE_ME",
        "INSERT_",
        "TODO:",
        "FIXME:",
    )
    for rel in repo.changed_files():
        normalized = rel.replace("\\", "/")
        if normalized in {".env", ".env.example"}:
            continue
        path = repo.root / rel
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for line_number, line in enumerate(text.splitlines(), start=1):
            if any(token in line for token in suspicious):
                findings.append(f"{normalized}:{line_number}: {line.strip()[:160]}")
    return {
        "name": "placeholder scan",
        "ok": not findings,
        "output": compact_output("\n".join(findings)),
    }


def compact_output(output: str, max_lines: int = 80) -> str:
    lines = [line for line in output.splitlines() if line.strip()]
    if len(lines) <= max_lines:
        return "\n".join(lines)
    return "\n".join([*lines[:20], "... output truncated ...", *lines[-60:]])


def fix_changed_file_whitespace(repo: GitRepo) -> None:
    for rel in repo.changed_files():
        if rel in {".env", ".env.example"}:
            continue
        path = repo.root / rel
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        lines = [line.rstrip() for line in text.splitlines()]
        while lines and lines[-1] == "":
            lines.pop()
        path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def fix_common_python_syntax_issues(root: Path) -> None:
    for path in root.rglob("*.py"):
        if any(part in {".git", ".venv", "__pycache__", ".agent_reports"} for part in path.parts):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        original = text
        text = text.replace("'''\\n\n", "'''\n\n").replace('"""\\n\n', '"""\n\n')

        future = "from __future__ import annotations"
        if future in text:
            lines = [line for line in text.splitlines() if line.strip() != future]
            text = future + "\n" + "\n".join(lines) + "\n"

        main_marker = 'if __name__ == "__main__":'
        first = text.find(main_marker)
        if first != -1:
            second = text.find(main_marker, first + len(main_marker))
            if second != -1:
                first_main_call = text.find("    main()", first)
                if first_main_call != -1 and first_main_call < second:
                    text = text[: first_main_call + len("    main()")] + "\n"

        if text != original:
            path.write_text(text, encoding="utf-8", newline="\n")
