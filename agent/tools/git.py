from __future__ import annotations

import subprocess
from pathlib import Path


class GitError(RuntimeError):
    pass


class GitRepo:
    def __init__(self, root: Path) -> None:
        self.root = root.expanduser().resolve()

    def run(self, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            ["git", *args],
            cwd=self.root,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            check=False,
        )
        if check and result.returncode != 0:
            message = result.stderr.strip() or result.stdout.strip()
            raise GitError(f"git {' '.join(args)} failed: {message}")
        return result

    def is_repo(self) -> bool:
        return self.run("rev-parse", "--is-inside-work-tree", check=False).returncode == 0

    def ensure_repo(self) -> None:
        if not self.is_repo():
            raise GitError(f"{self.root} is not a git repository.")

    def current_branch(self) -> str:
        self.ensure_repo()
        return self.run("branch", "--show-current").stdout.strip() or "HEAD"

    def checkout_branch(self, branch: str) -> str:
        self.ensure_repo()
        exists = self.run("rev-parse", "--verify", branch, check=False).returncode == 0
        if exists:
            self.run("checkout", branch)
        else:
            self.run("checkout", "-b", branch)
        return self.current_branch()

    def root_commit(self) -> str:
        self.ensure_repo()
        output = self.run("rev-list", "--max-parents=0", "HEAD").stdout.splitlines()
        if not output:
            raise GitError("Cannot determine repository root commit.")
        return output[0].strip()

    def branch_exists(self, branch: str) -> bool:
        self.ensure_repo()
        return self.run("rev-parse", "--verify", branch, check=False).returncode == 0

    def remote_branch_exists(self, branch: str, remote: str = "origin") -> bool:
        self.ensure_repo()
        ref = f"refs/remotes/{remote}/{branch}"
        return self.run("rev-parse", "--verify", ref, check=False).returncode == 0

    def checkout_branch_from(self, branch: str, start_point: str, remote: str = "origin") -> str:
        self.ensure_repo()
        if self.branch_exists(branch):
            self.run("checkout", branch)
        else:
            if not self.remote_branch_exists(branch, remote=remote):
                self.run("fetch", remote, branch, check=False)
            if self.remote_branch_exists(branch, remote=remote):
                self.run("checkout", "-b", branch, f"{remote}/{branch}")
            else:
                self.run("checkout", "-b", branch, start_point)
        return self.current_branch()

    def fetch_branch(self, branch: str, remote: str = "origin") -> None:
        self.ensure_repo()
        self.run("fetch", remote, branch, check=False)

    def is_clean(self) -> bool:
        self.ensure_repo()
        return not self.run("status", "--porcelain").stdout.strip()

    def reset_hard(self, target: str) -> None:
        self.ensure_repo()
        self.run("reset", "--hard", target)

    def clean_untracked(self) -> None:
        self.ensure_repo()
        self.run("clean", "-fd")

    def changed_files(self) -> list[str]:
        self.ensure_repo()
        output = self.run("status", "--short").stdout.splitlines()
        return sorted({line[3:].strip().replace("\\", "/") for line in output if len(line) > 3})

    def diff(self) -> str:
        self.ensure_repo()
        tracked_diff = self.run("diff", "--", ".").stdout
        untracked = self.untracked_files()
        if not untracked:
            return tracked_diff
        sections = [tracked_diff] if tracked_diff else []
        for rel in untracked:
            path = self.root / rel
            if not path.is_file():
                continue
            try:
                content = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            sections.append(f"diff --git a/{rel} b/{rel}\nnew file mode 100644\n--- /dev/null\n+++ b/{rel}\n")
            sections.append("".join(f"+{line}\n" for line in content.splitlines()))
        return "".join(sections)

    def untracked_files(self) -> list[str]:
        self.ensure_repo()
        output = self.run("ls-files", "--others", "--exclude-standard").stdout.splitlines()
        return sorted(line.strip().replace("\\", "/") for line in output if line.strip())

    def diff_check(self) -> tuple[bool, str]:
        self.ensure_repo()
        result = self.run("diff", "--check", check=False)
        return result.returncode == 0, result.stdout + result.stderr

    def commit_files(self, files: list[str], message: str, author_name: str, author_email: str) -> str:
        self.ensure_repo()
        if not files:
            raise GitError("No changed files to commit.")
        self.run("add", "--", *files)
        self.run(
            "-c",
            f"user.name={author_name}",
            "-c",
            f"user.email={author_email}",
            "commit",
            "-m",
            message,
        )
        return self.run("rev-parse", "HEAD").stdout.strip()

    def head_sha(self) -> str:
        self.ensure_repo()
        return self.run("rev-parse", "HEAD").stdout.strip()

    def remote_url(self) -> str:
        self.ensure_repo()
        result = self.run("remote", "get-url", "origin", check=False)
        return result.stdout.strip() if result.returncode == 0 else ""

    def ensure_origin(self, remote_url: str) -> str:
        self.ensure_repo()
        remote_url = remote_url.strip()
        if not remote_url:
            raise GitError("GITHUB_REPO_URL is required before pushing.")
        current = self.remote_url()
        if current:
            if current != remote_url:
                self.run("remote", "set-url", "origin", remote_url)
        else:
            self.run("remote", "add", "origin", remote_url)
        return remote_url

    def push(self, branch: str, *, force_with_lease: bool = False) -> str:
        self.ensure_repo()
        if force_with_lease:
            self.fetch_branch(branch)
        args = ["push", "-u"]
        if force_with_lease:
            args.append("--force-with-lease")
        args.extend(["origin", branch])
        result = self.run(*args, check=False)
        if result.returncode != 0 and force_with_lease and "stale info" in (result.stderr + result.stdout):
            self.fetch_branch(branch)
            result = self.run(*args, check=False)
        if result.returncode != 0:
            message = result.stderr.strip() or result.stdout.strip()
            raise GitError(f"git {' '.join(args)} failed: {message}")
        return branch
