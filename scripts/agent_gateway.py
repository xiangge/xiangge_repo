#!/usr/bin/env python3
"""Local GitHub issue gateway for Codex/Hermes agent jobs.

The gateway is intentionally small: it validates incoming issue events, creates
one managed checkout per repository, runs a local agent in that checkout, then
publishes the resulting spec branch and pull request.
"""

from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import threading
import time
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any


DONE_STATUSES = {"queued", "running", "done"}
REPO_LOCKS: dict[str, threading.Lock] = {}
REPO_LOCKS_GUARD = threading.Lock()


def parse_csv(value: str | None) -> set[str]:
    if not value:
        return set()
    return {item.strip() for item in value.split(",") if item.strip()}


def repo_key(repo: str) -> str:
    return repo.strip().lower()


def parse_repo_allowlist(value: str | None) -> set[str]:
    return {repo_key(item) for item in parse_csv(value)}


def parse_repo_urls(value: str | None) -> dict[str, str]:
    if not value:
        return {}

    value = value.strip()
    if not value:
        return {}

    if value.startswith("{"):
        parsed = json.loads(value)
        if not isinstance(parsed, dict):
            raise ValueError("GATEWAY_REPO_URLS JSON must be an object")
        return {repo_key(str(repo)): str(url).strip() for repo, url in parsed.items() if str(url).strip()}

    repo_urls: dict[str, str] = {}
    for item in value.split(","):
        item = item.strip()
        if not item:
            continue
        if "=" not in item:
            raise ValueError("GATEWAY_REPO_URLS entries must use owner/repo=url")
        repo, url = item.split("=", 1)
        if not repo.strip() or not url.strip():
            raise ValueError("GATEWAY_REPO_URLS entries must include both repo and URL")
        repo_urls[repo_key(repo)] = url.strip()
    return repo_urls


def bool_env(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


def slugify(value: str, fallback: str = "item") -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", value).strip("-").lower()
    return slug[:80] or fallback


def repo_lock(repo: str) -> threading.Lock:
    with REPO_LOCKS_GUARD:
        if repo not in REPO_LOCKS:
            REPO_LOCKS[repo] = threading.Lock()
        return REPO_LOCKS[repo]


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(path)


@dataclass(frozen=True)
class Config:
    host: str
    port: int
    work_root: Path
    allowed_repos: set[str]
    allow_any_repo: bool
    bearer_token: str | None
    webhook_secret: str | None
    allow_insecure: bool
    issue_actions: set[str]
    done_label: str
    agent_command: str | None
    codex_bin: str | None
    agent_timeout_seconds: int
    auto_pr: bool
    force_push: bool
    use_ssh: bool
    repo_urls: dict[str, str]
    repo_url_override: str | None
    sync: bool
    dry_run: bool

    @classmethod
    def from_env(cls, args: argparse.Namespace) -> "Config":
        return cls(
            host=args.host or os.getenv("GATEWAY_HOST", "127.0.0.1"),
            port=args.port or int(os.getenv("GATEWAY_PORT", "8787")),
            work_root=Path(os.getenv("GATEWAY_WORK_ROOT", ".agent-gateway")).resolve(),
            allowed_repos=parse_repo_allowlist(os.getenv("GATEWAY_ALLOWED_REPOS")),
            allow_any_repo=bool_env("GATEWAY_ALLOW_ANY_REPO"),
            bearer_token=os.getenv("GATEWAY_BEARER_TOKEN"),
            webhook_secret=os.getenv("GITHUB_WEBHOOK_SECRET"),
            allow_insecure=bool_env("GATEWAY_ALLOW_INSECURE"),
            issue_actions=parse_csv(os.getenv("GATEWAY_ISSUE_ACTIONS")) or {"opened"},
            done_label=os.getenv("GATEWAY_DONE_LABEL", "codex:spec-created"),
            agent_command=os.getenv("GATEWAY_AGENT_COMMAND"),
            codex_bin=os.getenv("GATEWAY_CODEX_BIN"),
            agent_timeout_seconds=int(os.getenv("GATEWAY_AGENT_TIMEOUT_SECONDS", "3600")),
            auto_pr=not bool_env("GATEWAY_NO_PR"),
            force_push=bool_env("GATEWAY_FORCE_PUSH"),
            use_ssh=not bool_env("GATEWAY_USE_HTTPS"),
            repo_urls=parse_repo_urls(os.getenv("GATEWAY_REPO_URLS")),
            repo_url_override=os.getenv("GATEWAY_REPO_URL"),
            sync=bool_env("GATEWAY_SYNC") or args.once is not None,
            dry_run=args.dry_run or bool_env("GATEWAY_DRY_RUN"),
        )

    def require_safe_repo_url_config(self) -> None:
        if self.repo_url_override and (self.allow_any_repo or len(self.allowed_repos) != 1):
            raise SystemExit(
                "GATEWAY_REPO_URL is only safe for one allowed repo. For multiple repos, "
                "use GATEWAY_REPO_URLS='owner/a=url,owner/b=url' or rely on GitHub payload URLs."
            )

    def require_safe_server_config(self) -> None:
        self.require_safe_repo_url_config()
        if not (self.bearer_token or self.webhook_secret or self.allow_insecure):
            raise SystemExit(
                "Refusing to start without auth. Set GATEWAY_BEARER_TOKEN, "
                "GITHUB_WEBHOOK_SECRET, or GATEWAY_ALLOW_INSECURE=1 for local-only tests."
            )
        if not (self.allowed_repos or self.allow_any_repo):
            raise SystemExit(
                "Refusing to start without repo allowlist. Set GATEWAY_ALLOWED_REPOS "
                "or GATEWAY_ALLOW_ANY_REPO=1 for local-only tests."
            )


@dataclass(frozen=True)
class Job:
    repo: str
    number: int
    title: str
    issue_url: str
    action: str
    default_branch: str
    clone_url: str
    ssh_url: str
    state_file: Path
    job_dir: Path
    issue_json: Path


def verify_signature(secret: str, body: bytes, signature: str | None) -> bool:
    if not signature or not signature.startswith("sha256="):
        return False
    digest = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(signature, f"sha256={digest}")


def is_authorized(config: Config, headers: Any, body: bytes) -> bool:
    authorization = headers.get("Authorization", "")
    if config.bearer_token and hmac.compare_digest(
        authorization,
        f"Bearer {config.bearer_token}",
    ):
        return True
    if config.webhook_secret and verify_signature(
        config.webhook_secret,
        body,
        headers.get("X-Hub-Signature-256"),
    ):
        return True
    return config.allow_insecure and not (config.bearer_token or config.webhook_secret)


def run_command(
    args: list[str] | str,
    cwd: Path,
    log_file: Path,
    env: dict[str, str] | None = None,
    timeout: int | None = None,
    shell: bool = False,
    allow_fail: bool = False,
    dry_run: bool = False,
) -> subprocess.CompletedProcess[str]:
    log_file.parent.mkdir(parents=True, exist_ok=True)
    rendered = args if isinstance(args, str) else " ".join(shlex.quote(part) for part in args)
    with log_file.open("a", encoding="utf-8") as log:
        log.write(f"\n$ {rendered}\n")

    if dry_run:
        return subprocess.CompletedProcess(args, 0, "", "")

    completed = subprocess.run(
        args,
        cwd=str(cwd),
        env=env,
        shell=shell,
        text=True,
        capture_output=True,
        timeout=timeout,
    )
    with log_file.open("a", encoding="utf-8") as log:
        if completed.stdout:
            log.write(completed.stdout)
        if completed.stderr:
            log.write(completed.stderr)
    if completed.returncode != 0 and not allow_fail:
        raise RuntimeError(f"Command failed ({completed.returncode}): {rendered}")
    return completed


def build_job(config: Config, payload: dict[str, Any]) -> tuple[Job | None, str]:
    action = payload.get("action", "")
    if action not in config.issue_actions:
        return None, f"ignored action {action!r}"

    issue = payload.get("issue") or {}
    if issue.get("pull_request"):
        return None, "ignored pull request issue payload"

    repo_data = payload.get("repository") or {}
    repo = repo_data.get("full_name", "")
    if not repo:
        raise ValueError("payload.repository.full_name is required")
    if not (config.allow_any_repo or repo_key(repo) in config.allowed_repos):
        raise PermissionError(f"repository is not allowed: {repo}")

    number = int(issue.get("number") or 0)
    if number <= 0:
        raise ValueError("payload.issue.number is required")

    labels = {label.get("name") for label in issue.get("labels", []) if isinstance(label, dict)}
    if config.done_label in labels:
        return None, f"ignored issue already labeled {config.done_label}"

    state_file = config.work_root / "state" / slugify(repo) / f"issue-{number}.json"
    if state_file.exists():
        try:
            state = json.loads(state_file.read_text(encoding="utf-8"))
            if state.get("status") in DONE_STATUSES:
                return None, f"ignored existing {state.get('status')} job"
        except json.JSONDecodeError:
            pass

    created = time.strftime("%Y%m%d-%H%M%S")
    job_dir = config.work_root / "jobs" / slugify(repo) / f"issue-{number}-{created}"
    issue_json = job_dir / "issue.json"
    default_branch = (
        repo_data.get("default_branch")
        or ((repo_data.get("defaultBranchRef") or {}).get("name"))
        or "main"
    )
    return (
        Job(
            repo=repo,
            number=number,
            title=issue.get("title") or f"Issue #{number}",
            issue_url=issue.get("html_url") or issue.get("url") or "",
            action=action,
            default_branch=default_branch,
            clone_url=repo_data.get("clone_url") or repo_data.get("url") or "",
            ssh_url=repo_data.get("ssh_url") or "",
            state_file=state_file,
            job_dir=job_dir,
            issue_json=issue_json,
        ),
        "queued",
    )


def resolve_repo_url(config: Config, job: Job) -> str:
    mapped_url = config.repo_urls.get(repo_key(job.repo))
    if mapped_url:
        return mapped_url
    if config.repo_url_override:
        return config.repo_url_override
    return job.ssh_url if config.use_ssh else job.clone_url


def prepare_repo(config: Config, job: Job, log_file: Path) -> Path:
    repo_dir = config.work_root / "repos" / slugify(job.repo)
    repo_url = resolve_repo_url(config, job)
    if not repo_url:
        raise ValueError("No repository clone URL found. Set GATEWAY_REPO_URLS or GATEWAY_REPO_URL.")

    if repo_dir.exists():
        run_command(["git", "remote", "set-url", "origin", repo_url], repo_dir, log_file, dry_run=config.dry_run)
        run_command(["git", "fetch", "origin"], repo_dir, log_file, dry_run=config.dry_run)
    else:
        repo_dir.parent.mkdir(parents=True, exist_ok=True)
        run_command(["git", "clone", repo_url, str(repo_dir)], config.work_root, log_file, dry_run=config.dry_run)

    repo_dir.mkdir(parents=True, exist_ok=True)
    run_command(["git", "checkout", job.default_branch], repo_dir, log_file, dry_run=config.dry_run)
    run_command(["git", "reset", "--hard", f"origin/{job.default_branch}"], repo_dir, log_file, dry_run=config.dry_run)
    return repo_dir


def branch_name(job: Job) -> str:
    return f"codex/issue-{job.number}-spec"


def spec_path(job: Job) -> str:
    return f"specs/issues/issue-{job.number}-{slugify(job.title, 'spec')}.md"


def codex_candidates(config: Config) -> list[str]:
    candidates: list[str] = []
    if config.codex_bin:
        candidates.append(config.codex_bin)
    path_codex = shutil.which("codex")
    if path_codex:
        candidates.append(path_codex)
    candidates.append("/Applications/ChatGPT.app/Contents/Resources/codex")

    seen: set[str] = set()
    unique_candidates: list[str] = []
    for candidate in candidates:
        if candidate in seen:
            continue
        seen.add(candidate)
        unique_candidates.append(candidate)
    return unique_candidates


def run_probe(args: list[str], cwd: Path, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(args, cwd=str(cwd), env=env, text=True, capture_output=True, timeout=30)
    except (FileNotFoundError, PermissionError) as exc:
        return subprocess.CompletedProcess(args, 127, "", str(exc))


def resolve_codex(config: Config, cwd: Path, env: dict[str, str], log_file: Path) -> str:
    errors: list[str] = []
    for candidate in codex_candidates(config):
        version = run_probe([candidate, "--version"], cwd, env)
        if version.returncode == 0:
            return candidate
        output = (version.stderr or version.stdout or "").strip()
        errors.append(f"{candidate}: {output or 'exit ' + str(version.returncode)}")
        if config.codex_bin:
            break

    with log_file.open("a", encoding="utf-8") as log:
        log.write("\nCodex binary probes failed:\n")
        for error in errors:
            log.write(f"- {error}\n")
    raise RuntimeError(
        "No working Codex CLI was found. Set GATEWAY_CODEX_BIN to a working binary "
        "or set GATEWAY_AGENT_COMMAND for Hermes."
    )


def codex_exec_owns_approval_flag(codex: str, cwd: Path, env: dict[str, str]) -> bool:
    help_result = run_probe([codex, "exec", "--help"], cwd, env)
    combined = f"{help_result.stdout}\n{help_result.stderr}"
    return "--ask-for-approval" in combined


def build_codex_command(codex: str, repo_dir: Path, prompt: str, env: dict[str, str]) -> list[str]:
    if codex_exec_owns_approval_flag(codex, repo_dir, env):
        return [
            codex,
            "exec",
            "--cd",
            str(repo_dir),
            "--sandbox",
            "workspace-write",
            "--ask-for-approval",
            "never",
            prompt,
        ]
    return [
        codex,
        "--ask-for-approval",
        "never",
        "exec",
        "--cd",
        str(repo_dir),
        "--sandbox",
        "workspace-write",
        prompt,
    ]


def run_agent(config: Config, job: Job, repo_dir: Path, log_file: Path) -> None:
    issue_text = job.issue_json.read_text(encoding="utf-8")
    prompt = f"""You are running from an automated GitHub issue gateway.

Issue JSON:
{issue_text}

Create or update this requirements spec file:
{spec_path(job)}

The spec should include: summary, goals, non-goals, user stories or acceptance criteria,
implementation notes, validation plan, and open questions.

Only edit files in this repository. Do not commit, push, create branches, create pull
requests, add labels, or comment on GitHub. The gateway will handle those side effects.
"""

    env = os.environ.copy()
    env.update(
        {
            "GATEWAY_REPO": job.repo,
            "GATEWAY_REPO_DIR": str(repo_dir),
            "GATEWAY_ISSUE_NUMBER": str(job.number),
            "GATEWAY_ISSUE_TITLE": job.title,
            "GATEWAY_ISSUE_URL": job.issue_url,
            "GATEWAY_ISSUE_JSON": str(job.issue_json),
            "GATEWAY_SPEC_PATH": spec_path(job),
        }
    )

    if config.agent_command:
        run_command(
            config.agent_command,
            repo_dir,
            log_file,
            env=env,
            timeout=config.agent_timeout_seconds,
            shell=True,
            dry_run=config.dry_run,
        )
        return

    codex = resolve_codex(config, repo_dir, env, log_file)
    run_command(
        build_codex_command(codex, repo_dir, prompt, env),
        repo_dir,
        log_file,
        env=env,
        timeout=config.agent_timeout_seconds,
        dry_run=config.dry_run,
    )


def publish_changes(config: Config, job: Job, repo_dir: Path, log_file: Path) -> str | None:
    status = run_command(["git", "status", "--porcelain"], repo_dir, log_file, dry_run=config.dry_run)
    if not status.stdout.strip() and not config.dry_run:
        raise RuntimeError("Agent completed but produced no repository changes.")

    gh = shutil.which("gh") or ("gh" if config.dry_run else None)
    if not gh:
        raise RuntimeError("gh CLI was not found. Install GitHub CLI or set GATEWAY_NO_PR=1.")

    branch = branch_name(job)
    run_command(["git", "add", "-A"], repo_dir, log_file, dry_run=config.dry_run)
    run_command(
        ["git", "commit", "-m", f"Spec for issue #{job.number}"],
        repo_dir,
        log_file,
        dry_run=config.dry_run,
    )
    push_args = ["git", "push", "-u", "origin", branch]
    if config.force_push:
        push_args.insert(2, "--force-with-lease")
    run_command(push_args, repo_dir, log_file, dry_run=config.dry_run)

    pr_body = job.job_dir / "pr-body.md"
    pr_body.write_text(
        f"Creates a requirements spec for #{job.number}.\n\nSource issue: {job.issue_url}\n",
        encoding="utf-8",
    )
    create = run_command(
        [
            gh,
            "pr",
            "create",
            "--repo",
            job.repo,
            "--base",
            job.default_branch,
            "--head",
            branch,
            "--title",
            f"Spec: {job.title}",
            "--body-file",
            str(pr_body),
        ],
        repo_dir,
        log_file,
        allow_fail=True,
        dry_run=config.dry_run,
    )
    pr_url = create.stdout.strip() if create.returncode == 0 else None
    if not pr_url and not config.dry_run:
        view = run_command(
            [gh, "pr", "view", branch, "--repo", job.repo, "--json", "url"],
            repo_dir,
            log_file,
            allow_fail=True,
        )
        if view.returncode == 0 and view.stdout.strip():
            pr_url = json.loads(view.stdout)["url"]

    if config.done_label:
        run_command(
            [
                gh,
                "label",
                "create",
                config.done_label,
                "--repo",
                job.repo,
                "--color",
                "5319e7",
                "--description",
                "Spec PR created by local agent gateway",
            ],
            repo_dir,
            log_file,
            allow_fail=True,
            dry_run=config.dry_run,
        )
        run_command(
            [gh, "issue", "edit", str(job.number), "--repo", job.repo, "--add-label", config.done_label],
            repo_dir,
            log_file,
            allow_fail=True,
            dry_run=config.dry_run,
        )
        comment = "Created a spec PR"
        if pr_url:
            comment += f": {pr_url}"
        run_command(
            [gh, "issue", "comment", str(job.number), "--repo", job.repo, "--body", comment],
            repo_dir,
            log_file,
            allow_fail=True,
            dry_run=config.dry_run,
        )

    return pr_url


def execute_job(config: Config, job: Job, payload: dict[str, Any]) -> None:
    log_file = job.job_dir / "gateway.log"
    write_json(job.issue_json, payload.get("issue") or {})
    write_json(
        job.state_file,
        {
            "status": "running",
            "repo": job.repo,
            "issue": job.number,
            "job_dir": str(job.job_dir),
            "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        },
    )

    try:
        with repo_lock(job.repo):
            repo_dir = prepare_repo(config, job, log_file)
            branch = branch_name(job)
            run_command(["git", "checkout", "-B", branch], repo_dir, log_file, dry_run=config.dry_run)
            run_agent(config, job, repo_dir, log_file)
            pr_url = publish_changes(config, job, repo_dir, log_file) if config.auto_pr else None

        write_json(
            job.state_file,
            {
                "status": "done",
                "repo": job.repo,
                "issue": job.number,
                "branch": branch_name(job),
                "pull_request": pr_url,
                "job_dir": str(job.job_dir),
                "finished_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            },
        )
    except Exception as exc:
        (job.job_dir / "error.txt").write_text(str(exc) + "\n", encoding="utf-8")
        write_json(
            job.state_file,
            {
                "status": "failed",
                "repo": job.repo,
                "issue": job.number,
                "job_dir": str(job.job_dir),
                "error": str(exc),
                "finished_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            },
        )
        raise


def schedule_or_run(config: Config, payload: dict[str, Any]) -> tuple[int, dict[str, Any]]:
    job, reason = build_job(config, payload)
    if job is None:
        return 200, {"status": "ignored", "reason": reason}

    write_json(
        job.state_file,
        {
            "status": "queued",
            "repo": job.repo,
            "issue": job.number,
            "job_dir": str(job.job_dir),
            "queued_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        },
    )

    if config.sync:
        execute_job(config, job, payload)
    else:
        thread = threading.Thread(target=execute_job, args=(config, job, payload), daemon=True)
        thread.start()
    return 202, {"status": "queued", "repo": job.repo, "issue": job.number, "job_dir": str(job.job_dir)}


class GatewayHandler(BaseHTTPRequestHandler):
    config: Config

    def log_message(self, fmt: str, *args: Any) -> None:
        sys.stderr.write(f"{self.address_string()} - {fmt % args}\n")

    def send_json(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        if self.path == "/healthz":
            self.send_json(200, {"status": "ok"})
            return
        self.send_json(404, {"error": "not found"})

    def do_POST(self) -> None:
        if self.path not in {"/github/issues", "/github/webhook"}:
            self.send_json(404, {"error": "not found"})
            return

        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0 or length > 2_000_000:
            self.send_json(413, {"error": "invalid body length"})
            return
        body = self.rfile.read(length)
        if not is_authorized(self.config, self.headers, body):
            self.send_json(401, {"error": "unauthorized"})
            return
        if self.headers.get("X-GitHub-Event", "issues") != "issues":
            self.send_json(200, {"status": "ignored", "reason": "not an issues event"})
            return

        try:
            payload = json.loads(body.decode("utf-8"))
            status, response = schedule_or_run(self.config, payload)
            self.send_json(status, response)
        except PermissionError as exc:
            self.send_json(403, {"error": str(exc)})
        except Exception as exc:
            self.send_json(500, {"error": str(exc)})


def serve(config: Config) -> None:
    config.require_safe_server_config()
    config.work_root.mkdir(parents=True, exist_ok=True)
    GatewayHandler.config = config
    server = ThreadingHTTPServer((config.host, config.port), GatewayHandler)
    print(f"agent gateway listening on http://{config.host}:{config.port}", flush=True)
    server.serve_forever()


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a local GitHub issue agent gateway.")
    parser.add_argument("--host", help="Bind host. Defaults to GATEWAY_HOST or 127.0.0.1.")
    parser.add_argument("--port", type=int, help="Bind port. Defaults to GATEWAY_PORT or 8787.")
    parser.add_argument("--once", type=Path, help="Process one GitHub issue event JSON and exit.")
    parser.add_argument("--dry-run", action="store_true", help="Log planned commands without running them.")
    args = parser.parse_args()

    config = Config.from_env(args)
    config.require_safe_repo_url_config()
    if args.once:
        payload = json.loads(args.once.read_text(encoding="utf-8"))
        status, response = schedule_or_run(config, payload)
        print(json.dumps({"http_status": status, **response}, ensure_ascii=False, indent=2))
        return 0

    serve(config)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
