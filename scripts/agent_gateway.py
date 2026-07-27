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
GATEWAY_COMMENT_MARKER = "<!-- agent-gateway -->"
DEFAULT_PR_ACTIONS = {"opened", "synchronize", "reopened", "ready_for_review"}
DEFAULT_COMMENT_ACTIONS = {"created", "edited"}
DEFAULT_ALLOWED_COMMENT_ASSOCIATIONS = {"OWNER", "MEMBER", "COLLABORATOR"}
BOT_USER_TYPES = {"Bot", "Mannequin"}


def parse_csv(value: str | None) -> set[str]:
    if not value:
        return set()
    return {item.strip() for item in value.split(",") if item.strip()}


def parse_upper_csv(value: str | None) -> set[str]:
    return {item.upper() for item in parse_csv(value)}


def parse_lower_csv(value: str | None) -> set[str]:
    return {item.lower() for item in parse_csv(value)}


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


def parse_json_map(value: str | None, env_name: str) -> dict[str, str]:
    if not value:
        return {}
    value = value.strip()
    if not value:
        return {}
    parsed = json.loads(value)
    if not isinstance(parsed, dict):
        raise ValueError(f"{env_name} JSON must be an object")
    return {repo_key(str(key)): str(item).strip() for key, item in parsed.items() if str(item).strip()}


def repo_value(values: dict[str, str], repo: str, fallback: str | None = None) -> str | None:
    return values.get(repo_key(repo)) or fallback


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
    pr_actions: set[str]
    comment_actions: set[str]
    allowed_comment_associations: set[str]
    allowed_comment_logins: set[str]
    done_label: str
    agent_command: str | None
    codex_bin: str | None
    agent_timeout_seconds: int
    stage_timeout_seconds: int
    pr_branch_prefix: str
    review_enabled: bool
    update_enabled: bool
    test_enabled: bool
    merge_enabled: bool
    test_command: str | None
    eval_command: str | None
    test_commands: dict[str, str]
    eval_commands: dict[str, str]
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
            pr_actions=parse_csv(os.getenv("GATEWAY_PR_ACTIONS")) or DEFAULT_PR_ACTIONS,
            comment_actions=parse_csv(os.getenv("GATEWAY_COMMENT_ACTIONS")) or DEFAULT_COMMENT_ACTIONS,
            allowed_comment_associations=parse_upper_csv(os.getenv("GATEWAY_ALLOWED_COMMENT_ASSOCIATIONS"))
            or DEFAULT_ALLOWED_COMMENT_ASSOCIATIONS,
            allowed_comment_logins=parse_lower_csv(os.getenv("GATEWAY_ALLOWED_COMMENT_LOGINS")),
            done_label=os.getenv("GATEWAY_DONE_LABEL", "codex:spec-created"),
            agent_command=os.getenv("GATEWAY_AGENT_COMMAND"),
            codex_bin=os.getenv("GATEWAY_CODEX_BIN"),
            agent_timeout_seconds=int(os.getenv("GATEWAY_AGENT_TIMEOUT_SECONDS", "3600")),
            stage_timeout_seconds=int(os.getenv("GATEWAY_STAGE_TIMEOUT_SECONDS", "3600")),
            pr_branch_prefix=os.getenv("GATEWAY_PR_BRANCH_PREFIX", "codex/issue-"),
            review_enabled=not bool_env("GATEWAY_REVIEW_DISABLED"),
            update_enabled=not bool_env("GATEWAY_UPDATE_DISABLED"),
            test_enabled=not bool_env("GATEWAY_TEST_DISABLED"),
            merge_enabled=not bool_env("GATEWAY_MERGE_DISABLED"),
            test_command=os.getenv("GATEWAY_TEST_COMMAND"),
            eval_command=os.getenv("GATEWAY_EVAL_COMMAND"),
            test_commands=parse_json_map(os.getenv("GATEWAY_TEST_COMMANDS"), "GATEWAY_TEST_COMMANDS"),
            eval_commands=parse_json_map(os.getenv("GATEWAY_EVAL_COMMANDS"), "GATEWAY_EVAL_COMMANDS"),
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


@dataclass(frozen=True)
class PrJob:
    repo: str
    number: int
    title: str
    pr_url: str
    action: str
    base_ref: str
    head_ref: str
    head_sha: str
    head_repo: str
    clone_url: str
    ssh_url: str
    body: str
    state_file: Path
    job_dir: Path
    payload_json: Path


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


def require_allowed_repo(config: Config, repo: str) -> None:
    if not repo:
        raise ValueError("repository full name is required")
    if not (config.allow_any_repo or repo_key(repo) in config.allowed_repos):
        raise PermissionError(f"repository is not allowed: {repo}")


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
    require_allowed_repo(config, repo)

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


def normalize_pr_payload(config: Config, payload: dict[str, Any]) -> tuple[PrJob | None, str]:
    action = payload.get("action", "")
    if action not in config.pr_actions and action not in {"manual", "comment"}:
        return None, f"ignored PR action {action!r}"

    pr = payload.get("pull_request") or {}
    if not pr:
        return None, "ignored payload without pull_request"

    repo_data = payload.get("repository") or {}
    repo = repo_data.get("full_name", "")
    require_allowed_repo(config, repo)

    number = int(pr.get("number") or 0)
    if number <= 0:
        raise ValueError("payload.pull_request.number is required")

    head = pr.get("head") or {}
    base = pr.get("base") or {}
    head_repo_data = head.get("repo") or {}
    head_ref = head.get("ref") or pr.get("headRefName") or ""
    head_sha = head.get("sha") or pr.get("headRefOid") or ""
    head_repo = head_repo_data.get("full_name") or pr.get("headRepositoryOwner", {}).get("login", "") + "/" + head_repo_data.get("name", "")
    head_repo = head_repo.strip("/")

    if config.pr_branch_prefix and head_ref and not head_ref.startswith(config.pr_branch_prefix):
        return None, f"ignored non-gateway branch {head_ref!r}"

    created = time.strftime("%Y%m%d-%H%M%S")
    key = head_sha or slugify(head_ref, "head")
    state_file = config.work_root / "pr-state" / slugify(repo) / f"pr-{number}" / f"{key}.json"
    job_dir = config.work_root / "pr-jobs" / slugify(repo) / f"pr-{number}-{created}"
    payload_json = job_dir / "payload.json"

    return (
        PrJob(
            repo=repo,
            number=number,
            title=pr.get("title") or f"PR #{number}",
            pr_url=pr.get("html_url") or pr.get("url") or "",
            action=action,
            base_ref=(base.get("ref") or pr.get("baseRefName") or repo_data.get("default_branch") or "main"),
            head_ref=head_ref,
            head_sha=head_sha,
            head_repo=head_repo or repo,
            clone_url=repo_data.get("clone_url") or repo_data.get("url") or "",
            ssh_url=repo_data.get("ssh_url") or "",
            body=pr.get("body") or "",
            state_file=state_file,
            job_dir=job_dir,
            payload_json=payload_json,
        ),
        "queued",
    )


def gh_bin(config: Config) -> str:
    gh = shutil.which("gh") or ("gh" if config.dry_run else None)
    if not gh:
        raise RuntimeError("gh CLI was not found. Install GitHub CLI.")
    return gh


def gh_json(config: Config, args: list[str], cwd: Path, log_file: Path) -> dict[str, Any]:
    completed = run_command([gh_bin(config), *args], cwd, log_file, dry_run=config.dry_run)
    if config.dry_run:
        return {}
    if not completed.stdout.strip():
        return {}
    return json.loads(completed.stdout)


def pr_payload_from_view(config: Config, repo: str, number: int, cwd: Path, log_file: Path) -> dict[str, Any]:
    pr = gh_json(
        config,
        [
            "pr",
            "view",
            str(number),
            "--repo",
            repo,
            "--json",
            "number,title,url,body,headRefName,headRefOid,baseRefName,state,isDraft",
        ],
        cwd,
        log_file,
    )
    repo_info = gh_json(
        config,
        ["repo", "view", repo, "--json", "nameWithOwner,sshUrl,url,defaultBranchRef"],
        cwd,
        log_file,
    )
    default_branch = (repo_info.get("defaultBranchRef") or {}).get("name") or "main"
    return {
        "action": "comment",
        "repository": {
            "full_name": repo_info.get("nameWithOwner") or repo,
            "ssh_url": repo_info.get("sshUrl") or "",
            "clone_url": repo_info.get("url") or "",
            "default_branch": default_branch,
        },
        "pull_request": {
            "number": pr.get("number") or number,
            "title": pr.get("title") or f"PR #{number}",
            "html_url": pr.get("url") or "",
            "body": pr.get("body") or "",
            "head": {"ref": pr.get("headRefName") or "", "sha": pr.get("headRefOid") or "", "repo": {"full_name": repo}},
            "base": {"ref": pr.get("baseRefName") or default_branch},
        },
    }
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


def run_codex_prompt(
    config: Config,
    repo_dir: Path,
    log_file: Path,
    prompt: str,
    env: dict[str, str],
    timeout: int | None = None,
) -> subprocess.CompletedProcess[str]:
    codex = resolve_codex(config, repo_dir, env, log_file)
    return run_command(
        build_codex_command(codex, repo_dir, prompt, env),
        repo_dir,
        log_file,
        env=env,
        timeout=timeout or config.agent_timeout_seconds,
        dry_run=config.dry_run,
    )


def run_agent(config: Config, job: Job, repo_dir: Path, log_file: Path) -> None:
    issue_text = job.issue_json.read_text(encoding="utf-8")
    prompt = f"""You are running from an automated GitHub issue gateway.

Issue JSON:
{issue_text}

Create or update this requirements spec file and keep it in the same PR as the
actual issue deliverables:
{spec_path(job)}

The spec should include: summary, goals, non-goals, user stories or acceptance criteria,
implementation notes, validation plan, and open questions.

Then implement the issue request itself in the same repository change. If the
issue asks for generated files, documents, reports, code, configuration, or a
final PDF, create or update those deliverables as repository files alongside the
spec. Keep the implementation aligned with the spec.

Do not add broad test suites or evaluation harnesses in this authoring step unless
the issue explicitly asks for them as the primary deliverable. A separate gated
stage will add tests/evals after a maintainer comments /ok-to-add-test.

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

    run_codex_prompt(config, repo_dir, log_file, prompt, env, config.agent_timeout_seconds)


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
        ["git", "commit", "-m", f"Implement issue #{job.number} with spec"],
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
        f"Implements #{job.number} with a requirements spec and the requested deliverables.\n\nSource issue: {job.issue_url}\n",
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
            f"Implement: {job.title}",
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
                "Implementation/spec PR created by local agent gateway",
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
        comment = "Created an implementation/spec PR"
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


def stage_key(pr: PrJob, stage: str, payload: dict[str, Any]) -> str:
    comment = payload.get("comment") or {}
    if stage in {"update", "test", "merge"} and comment.get("id"):
        return f"comment-{comment['id']}"
    return pr.head_sha or slugify(pr.head_ref, "head")


def stage_paths(config: Config, pr: PrJob, stage: str, key: str) -> tuple[Path, Path, Path]:
    state_file = config.work_root / "stage-state" / slugify(pr.repo) / f"pr-{pr.number}" / key / f"{stage}.json"
    run_dir = config.work_root / "stage-runs" / slugify(pr.repo) / f"pr-{pr.number}" / key / stage
    payload_file = run_dir / "payload.json"
    return state_file, run_dir, payload_file


def resolve_pr_repo_url(config: Config, pr: PrJob) -> str:
    mapped_url = config.repo_urls.get(repo_key(pr.repo))
    if mapped_url:
        return mapped_url
    if config.repo_url_override:
        return config.repo_url_override
    return pr.ssh_url if config.use_ssh else pr.clone_url


def prepare_pr_stage_repo(config: Config, pr: PrJob, run_dir: Path, log_file: Path) -> Path:
    repo_dir = run_dir / "repo"
    repo_url = resolve_pr_repo_url(config, pr)
    if not repo_url:
        raise ValueError("No repository clone URL found for PR stage. Set GATEWAY_REPO_URLS.")

    if repo_dir.exists():
        run_command(["git", "remote", "set-url", "origin", repo_url], repo_dir, log_file, dry_run=config.dry_run)
        run_command(["git", "fetch", "origin"], repo_dir, log_file, dry_run=config.dry_run)
    else:
        repo_dir.parent.mkdir(parents=True, exist_ok=True)
        run_command(["git", "clone", repo_url, str(repo_dir)], run_dir, log_file, dry_run=config.dry_run)

    repo_dir.mkdir(parents=True, exist_ok=True)
    run_command(["git", "fetch", "origin", f"refs/pull/{pr.number}/head:gateway-pr-{pr.number}"], repo_dir, log_file, dry_run=config.dry_run)
    run_command(["git", "fetch", "origin", pr.base_ref], repo_dir, log_file, dry_run=config.dry_run)
    run_command(["git", "checkout", "-B", f"gateway-pr-{pr.number}", f"gateway-pr-{pr.number}"], repo_dir, log_file, dry_run=config.dry_run)
    return repo_dir


def comment_body(title: str, body: str) -> str:
    max_body = 58_000
    if len(body) > max_body:
        body = body[:max_body] + "\n\n[truncated by gateway]"
    return f"{GATEWAY_COMMENT_MARKER}\n### {title}\n\n{body}"


def post_pr_comment(config: Config, pr: PrJob, title: str, body: str, cwd: Path, log_file: Path) -> None:
    comment_file = log_file.parent / f"{slugify(title)}-comment.md"
    comment_file.write_text(comment_body(title, body), encoding="utf-8")
    run_command(
        [gh_bin(config), "pr", "comment", str(pr.number), "--repo", pr.repo, "--body-file", str(comment_file)],
        cwd,
        log_file,
        allow_fail=True,
        dry_run=config.dry_run,
    )


def commit_and_push_stage_changes(
    config: Config,
    pr: PrJob,
    repo_dir: Path,
    log_file: Path,
    message: str,
) -> bool:
    status = run_command(["git", "status", "--porcelain"], repo_dir, log_file, dry_run=config.dry_run)
    if not status.stdout.strip() and not config.dry_run:
        return False
    run_command(["git", "add", "-A"], repo_dir, log_file, dry_run=config.dry_run)
    run_command(["git", "commit", "-m", message], repo_dir, log_file, dry_run=config.dry_run)
    run_command(["git", "push", "origin", f"HEAD:{pr.head_ref}"], repo_dir, log_file, dry_run=config.dry_run)
    return True


def stage_env(pr: PrJob, repo_dir: Path, payload_file: Path) -> dict[str, str]:
    env = os.environ.copy()
    env.update(
        {
            "GATEWAY_REPO": pr.repo,
            "GATEWAY_REPO_DIR": str(repo_dir),
            "GATEWAY_PR_NUMBER": str(pr.number),
            "GATEWAY_PR_TITLE": pr.title,
            "GATEWAY_PR_URL": pr.pr_url,
            "GATEWAY_PR_BASE_REF": pr.base_ref,
            "GATEWAY_PR_HEAD_REF": pr.head_ref,
            "GATEWAY_PR_HEAD_SHA": pr.head_sha,
            "GATEWAY_PAYLOAD_JSON": str(payload_file),
        }
    )
    return env


def run_review_stage(config: Config, pr: PrJob, repo_dir: Path, payload_file: Path, log_file: Path) -> None:
    env = stage_env(pr, repo_dir, payload_file)
    prompt = f"""You are an independent PR review agent. Do not edit files.

Review PR #{pr.number} in {pr.repo}: {pr.title}
PR URL: {pr.pr_url}

Review both the implementation and the spec files. Compare the diff against
origin/{pr.base_ref}. Check whether the issue requirements are reflected in the
spec and in the actual deliverables. If the issue asked for generated files,
documents, code, or PDFs, verify those deliverables are present and aligned.

Prioritize correctness bugs, missing issue requirements, missing deliverables,
spec mismatches, safety/security risks, and obvious test/evaluation gaps.

Output:
- If changes are incorrect or incomplete, list actionable findings and required fixes.
- If it looks correct, say APPROVED and mention remaining risks briefly.
"""
    completed = run_codex_prompt(config, repo_dir, log_file, prompt, env, config.stage_timeout_seconds)
    review = (completed.stdout or completed.stderr or "Review completed; see gateway log.").strip()
    post_pr_comment(config, pr, "Gateway review", review, repo_dir, log_file)


def run_update_stage(config: Config, pr: PrJob, repo_dir: Path, payload: dict[str, Any], payload_file: Path, log_file: Path) -> None:
    comment = payload.get("comment") or {}
    body = comment.get("body") or ""
    env = stage_env(pr, repo_dir, payload_file)
    env.update(
        {
            "GATEWAY_COMMENT_ID": str(comment.get("id") or ""),
            "GATEWAY_COMMENT_BODY": body,
            "GATEWAY_COMMENT_URL": comment.get("html_url") or "",
        }
    )
    prompt = f"""You are an independent PR update agent. Apply the maintainer feedback comment
to PR #{pr.number} in {pr.repo}. This is a new agent session and a separate checkout.

Maintainer comment:
{body}

Rules:
- Update code/spec/docs/generated files as needed to satisfy the comment.
- Keep the spec and implementation synchronized.
- Do not add broad test/eval suites here unless the comment explicitly asks for a
  deliverable. The /ok-to-add-test command is handled by a separate test stage.
- Do not commit, push, comment, or merge; the gateway handles side effects.
"""
    run_codex_prompt(config, repo_dir, log_file, prompt, env, config.stage_timeout_seconds)
    changed = commit_and_push_stage_changes(config, pr, repo_dir, log_file, f"Apply feedback on PR #{pr.number}")
    if changed:
        post_pr_comment(config, pr, "Gateway update", f"Applied feedback from comment {comment.get('html_url') or comment.get('id')}.", repo_dir, log_file)
    else:
        post_pr_comment(config, pr, "Gateway update", "No repository changes were produced for that feedback comment.", repo_dir, log_file)


def run_shell_stage_command(config: Config, pr: PrJob, repo_dir: Path, log_file: Path, command: str | None, label: str) -> tuple[bool, str]:
    if not command:
        return True, f"{label}: no command configured."
    completed = run_command(command, repo_dir, log_file, shell=True, allow_fail=True, dry_run=config.dry_run)
    output = "\n".join(part for part in [completed.stdout, completed.stderr] if part).strip()
    if config.dry_run:
        return True, f"{label}: dry-run command planned: `{command}`"
    if completed.returncode == 0:
        return True, f"{label}: passed.\n\n```\n{output[-4000:]}\n```" if output else f"{label}: passed."
    return False, f"{label}: failed with exit code {completed.returncode}.\n\n```\n{output[-8000:]}\n```"


def run_test_stage(config: Config, pr: PrJob, repo_dir: Path, payload_file: Path, log_file: Path) -> None:
    env = stage_env(pr, repo_dir, payload_file)
    prompt = f"""You are an independent test/evaluation agent for PR #{pr.number} in {pr.repo}.

The maintainer has approved adding tests/evals with /ok-to-add-test.

Add or update focused tests, fixtures, examples, or evaluation files that validate
the issue requirements, spec, and implementation. Keep the changes narrow and
aligned with the PR. Do not commit, push, comment, or merge; the gateway handles
side effects.
"""
    run_codex_prompt(config, repo_dir, log_file, prompt, env, config.stage_timeout_seconds)

    test_command = repo_value(config.test_commands, pr.repo, config.test_command)
    eval_command = repo_value(config.eval_commands, pr.repo, config.eval_command)
    test_ok, test_summary = run_shell_stage_command(config, pr, repo_dir, log_file, test_command, "Test")
    eval_ok, eval_summary = run_shell_stage_command(config, pr, repo_dir, log_file, eval_command, "Eval")

    changed = False
    if test_ok and eval_ok:
        changed = commit_and_push_stage_changes(config, pr, repo_dir, log_file, f"Add tests for PR #{pr.number}")

    summary = f"{test_summary}\n\n{eval_summary}"
    if changed:
        summary += "\n\nPushed test/eval updates to the PR branch."
    elif test_ok and eval_ok:
        summary += "\n\nNo test/eval repository changes were produced."
    else:
        summary += "\n\nDid not push test/eval changes because at least one command failed."
    post_pr_comment(config, pr, "Gateway test/eval", summary, repo_dir, log_file)


def run_merge_stage(config: Config, pr: PrJob, repo_dir: Path, log_file: Path) -> None:
    completed = run_command(
        [gh_bin(config), "pr", "merge", str(pr.number), "--repo", pr.repo, "--squash", "--delete-branch"],
        repo_dir,
        log_file,
        allow_fail=True,
        dry_run=config.dry_run,
    )
    output = "\n".join(part for part in [completed.stdout, completed.stderr] if part).strip()
    if config.dry_run or completed.returncode == 0:
        post_pr_comment(config, pr, "Gateway merge", "Squash merge completed.", repo_dir, log_file)
    else:
        post_pr_comment(config, pr, "Gateway merge failed", f"Squash merge failed.\n\n```\n{output[-8000:]}\n```", repo_dir, log_file)


def execute_pr_stage(config: Config, pr: PrJob, stage: str, payload: dict[str, Any], state_file: Path, run_dir: Path, payload_file: Path) -> None:
    log_file = run_dir / "gateway.log"
    write_json(payload_file, payload)
    write_json(
        state_file,
        {
            "status": "running",
            "repo": pr.repo,
            "pr": pr.number,
            "stage": stage,
            "head_sha": pr.head_sha,
            "run_dir": str(run_dir),
            "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        },
    )

    try:
        with repo_lock(f"{pr.repo}:pr-{pr.number}"):
            repo_dir = prepare_pr_stage_repo(config, pr, run_dir, log_file)
            if stage == "review":
                run_review_stage(config, pr, repo_dir, payload_file, log_file)
            elif stage == "update":
                run_update_stage(config, pr, repo_dir, payload, payload_file, log_file)
            elif stage == "test":
                run_test_stage(config, pr, repo_dir, payload_file, log_file)
            elif stage == "merge":
                run_merge_stage(config, pr, repo_dir, log_file)
            else:
                raise ValueError(f"unknown stage: {stage}")

        write_json(
            state_file,
            {
                "status": "done",
                "repo": pr.repo,
                "pr": pr.number,
                "stage": stage,
                "head_sha": pr.head_sha,
                "run_dir": str(run_dir),
                "finished_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            },
        )
    except Exception as exc:
        run_dir.mkdir(parents=True, exist_ok=True)
        (run_dir / "error.txt").write_text(str(exc) + "\n", encoding="utf-8")
        write_json(
            state_file,
            {
                "status": "failed",
                "repo": pr.repo,
                "pr": pr.number,
                "stage": stage,
                "head_sha": pr.head_sha,
                "run_dir": str(run_dir),
                "error": str(exc),
                "finished_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            },
        )
        raise


def enqueue_pr_stage(config: Config, pr: PrJob, stage: str, payload: dict[str, Any]) -> tuple[int, dict[str, Any]]:
    key = stage_key(pr, stage, payload)
    state_file, run_dir, payload_file = stage_paths(config, pr, stage, key)
    if state_file.exists():
        try:
            state = json.loads(state_file.read_text(encoding="utf-8"))
            if state.get("status") in DONE_STATUSES:
                return 200, {"status": "ignored", "reason": f"{stage} already {state.get('status')}", "stage": stage}
        except json.JSONDecodeError:
            pass

    write_json(
        state_file,
        {
            "status": "queued",
            "repo": pr.repo,
            "pr": pr.number,
            "stage": stage,
            "head_sha": pr.head_sha,
            "run_dir": str(run_dir),
            "queued_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        },
    )

    if config.sync:
        execute_pr_stage(config, pr, stage, payload, state_file, run_dir, payload_file)
    else:
        thread = threading.Thread(
            target=execute_pr_stage,
            args=(config, pr, stage, payload, state_file, run_dir, payload_file),
            daemon=True,
        )
        thread.start()
    return 202, {"status": "queued", "repo": pr.repo, "pr": pr.number, "stage": stage, "run_dir": str(run_dir)}


def schedule_pr_event(config: Config, payload: dict[str, Any]) -> tuple[int, dict[str, Any]]:
    pr, reason = normalize_pr_payload(config, payload)
    if pr is None:
        return 200, {"status": "ignored", "reason": reason}
    if not config.review_enabled:
        return 200, {"status": "ignored", "reason": "review disabled"}
    return enqueue_pr_stage(config, pr, "review", payload)


def comment_is_from_gateway(payload: dict[str, Any]) -> bool:
    comment = payload.get("comment") or {}
    body = comment.get("body") or ""
    user_type = ((comment.get("user") or {}).get("type") or "").strip()
    return GATEWAY_COMMENT_MARKER in body or user_type in BOT_USER_TYPES


def comment_author_is_allowed(config: Config, payload: dict[str, Any]) -> bool:
    comment = payload.get("comment") or {}
    user = comment.get("user") or {}
    login = (user.get("login") or "").strip().lower()
    association = (comment.get("author_association") or "").strip().upper()
    if config.allowed_comment_logins and login in config.allowed_comment_logins:
        return True
    return association in config.allowed_comment_associations


def schedule_comment_event(config: Config, payload: dict[str, Any]) -> tuple[int, dict[str, Any]]:
    action = payload.get("action", "")
    if action not in config.comment_actions:
        return 200, {"status": "ignored", "reason": f"ignored comment action {action!r}"}
    if comment_is_from_gateway(payload):
        return 200, {"status": "ignored", "reason": "gateway/bot comment"}
    if not comment_author_is_allowed(config, payload):
        return 200, {"status": "ignored", "reason": "comment author is not allowed to trigger gateway stages"}

    issue = payload.get("issue") or {}
    if not issue.get("pull_request"):
        return 200, {"status": "ignored", "reason": "not a PR comment"}

    repo = (payload.get("repository") or {}).get("full_name", "")
    require_allowed_repo(config, repo)
    pr_number = int(issue.get("number") or 0)
    if pr_number <= 0:
        raise ValueError("payload.issue.number is required for PR comments")

    comment = payload.get("comment") or {}
    body = (comment.get("body") or "").strip()
    if payload.get("pull_request"):
        pr_payload = {
            "action": "comment",
            "repository": payload.get("repository") or {},
            "pull_request": payload.get("pull_request") or {},
        }
    else:
        helper_log = config.work_root / "comment-lookup" / slugify(repo) / f"pr-{pr_number}.log"
        pr_payload = pr_payload_from_view(config, repo, pr_number, config.work_root, helper_log)
    pr_payload["comment"] = comment
    pr_payload["action"] = "comment"
    pr, reason = normalize_pr_payload(config, pr_payload)
    if pr is None:
        return 200, {"status": "ignored", "reason": reason}

    if body.startswith("/ok-to-add-test"):
        if not config.test_enabled:
            return 200, {"status": "ignored", "reason": "test stage disabled"}
        return enqueue_pr_stage(config, pr, "test", pr_payload)
    if body.startswith("/ok-to-merge"):
        if not config.merge_enabled:
            return 200, {"status": "ignored", "reason": "merge stage disabled"}
        return enqueue_pr_stage(config, pr, "merge", pr_payload)

    if not config.update_enabled:
        return 200, {"status": "ignored", "reason": "update stage disabled"}
    return enqueue_pr_stage(config, pr, "update", pr_payload)


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
        allowed_paths = {"/github/issues", "/github/pull-requests", "/github/comments", "/github/webhook"}
        if self.path not in allowed_paths:
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
        event = self.headers.get("X-GitHub-Event", "issues")

        try:
            payload = json.loads(body.decode("utf-8"))
            if self.path == "/github/issues" or (self.path == "/github/webhook" and event == "issues"):
                status, response = schedule_or_run(self.config, payload)
            elif self.path == "/github/pull-requests" or (self.path == "/github/webhook" and event == "pull_request"):
                status, response = schedule_pr_event(self.config, payload)
            elif self.path == "/github/comments" or (self.path == "/github/webhook" and event == "issue_comment"):
                status, response = schedule_comment_event(self.config, payload)
            else:
                status, response = 200, {"status": "ignored", "reason": f"unsupported event {event!r}"}
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
    config.work_root.mkdir(parents=True, exist_ok=True)
    if args.once:
        payload = json.loads(args.once.read_text(encoding="utf-8"))
        if payload.get("comment") and payload.get("issue"):
            status, response = schedule_comment_event(config, payload)
        elif payload.get("pull_request"):
            status, response = schedule_pr_event(config, payload)
        else:
            status, response = schedule_or_run(config, payload)
        print(json.dumps({"http_status": status, **response}, ensure_ascii=False, indent=2))
        return 0

    serve(config)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
