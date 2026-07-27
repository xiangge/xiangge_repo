# xiangge_repo

Personal projects for testing.

## Agent gateway

This repo includes a GitHub issue/PR gateway that lets GitHub Actions trigger a
local Codex or Hermes agent. The gateway is intended to serve both
`xiangge/finding-jobs` and `xiangge/gravity-shift` from one local machine.

### Process

```text
Issue opened
  -> GitHub Actions sends the issue payload to the local gateway
  -> local agent creates the requirements spec and the requested deliverables
  -> gateway pushes a branch and opens a PR

PR opened or updated
  -> GitHub Actions sends the PR payload to the local gateway
  -> an independent review worker checks code, spec, and deliverables
  -> gateway leaves a PR comment with review findings

PR comment
  -> normal maintainer comment triggers an independent update worker
  -> /ok-to-add-test triggers an independent test/eval worker
  -> /ok-to-merge triggers a squash merge
```

The initial issue worker must include the issue-requested work in the same PR as
the spec. For example, if an issue asks for generated files, documentation, code,
or a final PDF, those deliverables should be committed with
`specs/issues/issue-<number>-<slug>.md`.

### GitHub setup

Each repo that should use the gateway needs these workflow files:

- `.github/workflows/issue-agent-gateway.yml`
- `.github/workflows/pr-agent-gateway.yml`

Each repo also needs these GitHub Actions secrets:

- `GATEWAY_URL`: public gateway URL, usually ending in `/github/issues`
- `GATEWAY_TOKEN`: token that matches local `GATEWAY_BEARER_TOKEN`

The PR workflow derives the PR and comment endpoints from `GATEWAY_URL`:

```text
https://your-gateway.example.com/github/pull-requests
https://your-gateway.example.com/github/comments
```

### Local gateway setup

Example local environment for the two repos:

```bash
export GATEWAY_ALLOWED_REPOS=xiangge/finding-jobs,xiangge/gravity-shift
export GATEWAY_BEARER_TOKEN='replace-with-a-long-random-token'
export GATEWAY_REPO_URLS='xiangge/finding-jobs=git@github.com:xiangge/finding-jobs.git,xiangge/gravity-shift=git@github.com:xiangge/gravity-shift.git'
export GATEWAY_ALLOWED_COMMENT_LOGINS=xiangge
export GATEWAY_HOST=127.0.0.1
export GATEWAY_PORT=8787

python3 scripts/agent_gateway.py
```

Optional per-repo test/eval commands:

```bash
export GATEWAY_TEST_COMMANDS='{"xiangge/finding-jobs":"pytest","xiangge/gravity-shift":"npm test"}'
export GATEWAY_EVAL_COMMANDS='{"xiangge/finding-jobs":"python evals/run_eval.py","xiangge/gravity-shift":"npm run eval"}'
```

If the Homebrew or npm `codex` wrapper is unavailable, point the gateway at the
Codex binary bundled with the ChatGPT app:

```bash
export GATEWAY_CODEX_BIN=/Applications/ChatGPT.app/Contents/Resources/codex
```

### Operational notes

- Use Cloudflare Tunnel, HTTPS reverse proxy, ngrok, or another secure tunnel
  when GitHub-hosted runners need to reach the local gateway.
- Do not expose the Codex/Hermes sandbox directly; expose only this gateway.
- PR comment triggers are limited to allowed maintainers by default. Set
  `GATEWAY_ALLOWED_COMMENT_LOGINS` to make the allowlist explicit.
- Gateway comments include `<!-- agent-gateway -->` and are ignored on the next
  comment webhook to avoid loops.
- The gateway serializes stages for the same PR, but different PRs/repos can run
  asynchronously.

Full setup and troubleshooting details are in `docs/agent-gateway.md`.
