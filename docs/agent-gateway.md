# GitHub issue 到本地 Agent Gateway

这套机制用于把 GitHub issue 事件实时转成本地 agent 任务：

```text
GitHub issue opened
  -> GitHub Actions workflow
  -> 本地 agent gateway
  -> Codex 或 Hermes 在本地 sandbox/checkout 里生成 spec
  -> gateway 提交分支、创建 PR、回写 issue label/comment
```

## 文件

- `.github/workflows/issue-agent-gateway.yml`：监听 issue opened，并把事件投递到 gateway。
- `scripts/agent_gateway.py`：本地 gateway，负责鉴权、排重、checkout、运行 agent、创建 PR。
- `.agent-gateway/`：运行时目录，保存 repo checkout、job log 和状态文件，已加入 `.gitignore`。

## GitHub secrets

在目标 repo 的 `Settings -> Secrets and variables -> Actions` 配置：

- `GATEWAY_URL`：gateway 公网地址，例如 `https://your-tunnel.example.com/github/issues` 或 `https://xxx.trycloudflare.com/github/issues`。
- `GATEWAY_TOKEN`：workflow 调用 gateway 的 bearer token。

workflow 只需要把 event 发给 gateway；真正的 repo 写权限和 agent 登录态在本地机器上。

## 本地启动

默认 agent 是 Codex CLI。先确保本机已经登录：

```bash
codex login status
gh auth status
```

真实创建分支、PR、label 和 comment 需要本机安装并登录 GitHub CLI。设置
`GATEWAY_NO_PR=1` 可以只运行 agent，不发布任何 GitHub 副作用。

如果 `codex` 的 Homebrew/npm wrapper 不可用，可以显式指定 ChatGPT App
内置的 Codex binary：

```bash
export GATEWAY_CODEX_BIN=/Applications/ChatGPT.app/Contents/Resources/codex
```

然后启动 gateway：

```bash
export GATEWAY_ALLOWED_REPOS=xiangge/gravity-shift
export GATEWAY_BEARER_TOKEN='replace-with-a-long-random-token'
export GATEWAY_HOST=127.0.0.1
export GATEWAY_PORT=8787

python3 scripts/agent_gateway.py
```

默认情况下，gateway 会使用 GitHub event payload 里的 `repository.ssh_url` 克隆仓库。
如果 payload 不包含 SSH 地址，或者你想显式指定 clone 地址，可以设置：

```bash
export GATEWAY_REPO_URL=git@github.com:xiangge/gravity-shift.git
```

`GATEWAY_REPO_URL` 只适合单 repo。多 repo 请使用下面的 `GATEWAY_REPO_URLS`。

如果这个 workflow 就运行在 self-hosted runner 上，可以把 URL 设置成本机地址：

```text
GATEWAY_URL=http://127.0.0.1:8787/github/issues
```

如果使用 GitHub-hosted runner，需要用 Cloudflare Tunnel、ngrok、Tailscale Funnel、反向代理等方式把 gateway 暴露出去。不要直接暴露 Codex/Hermes sandbox，只暴露这个受限 gateway。

## 多 repo

同一个本地 gateway 可以服务多个 repo。把 repo 全名加入 allowlist：

```bash
export GATEWAY_ALLOWED_REPOS=xiangge/gravity-shift,xiangge/another-private-repo,other-org/service-api
export GATEWAY_BEARER_TOKEN='replace-with-a-long-random-token'
python3 scripts/agent_gateway.py
```

每个 repo 的 GitHub workflow 或 webhook 都可以使用同一个公网入口：

```text
GATEWAY_URL=https://gateway.example.com/github/issues
GATEWAY_TOKEN=和本地 GATEWAY_BEARER_TOKEN 一样
```

gateway 会按 payload 里的 `repository.full_name` 分流：

- `.agent-gateway/repos/<repo-slug>/`：每个 repo 一个本地 checkout。
- `.agent-gateway/jobs/<repo-slug>/`：每个 repo 独立 job log。
- `.agent-gateway/state/<repo-slug>/`：每个 repo 独立排重状态。

如果要显式指定每个 repo 的 SSH URL，用逗号分隔的映射：

```bash
export GATEWAY_REPO_URLS='xiangge/gravity-shift=git@github.com:xiangge/gravity-shift.git,xiangge/another-private-repo=git@github.com:xiangge/another-private-repo.git'
```

也可以用 JSON，适合 URL 较多时更清楚：

```bash
export GATEWAY_REPO_URLS='{
  "xiangge/gravity-shift": "git@github.com:xiangge/gravity-shift.git",
  "xiangge/another-private-repo": "git@github.com:xiangge/another-private-repo.git"
}'
```

多 repo 模式下不要设置 `GATEWAY_REPO_URL`，否则 gateway 会拒绝启动，避免所有 repo 都被错误地 clone 到同一个地址。

注意：workflow 监听的是它所在 repo 的 issue。要让多个 repo 都触发同一个本地 gateway，需要在每个目标 repo 放一个薄 workflow，或者在每个目标 repo 的 GitHub Webhook 里直接 POST 到同一个 `GATEWAY_URL`。

## 接 Hermes

默认命令是 `codex exec`。如果要换成 Hermes，设置 `GATEWAY_AGENT_COMMAND`：

```bash
export GATEWAY_AGENT_COMMAND='hermes run --repo "$GATEWAY_REPO_DIR" --issue "$GATEWAY_ISSUE_JSON" --out "$GATEWAY_SPEC_PATH"'
python3 scripts/agent_gateway.py
```

gateway 会给命令注入这些环境变量：

- `GATEWAY_REPO`
- `GATEWAY_REPO_DIR`
- `GATEWAY_ISSUE_NUMBER`
- `GATEWAY_ISSUE_TITLE`
- `GATEWAY_ISSUE_URL`
- `GATEWAY_ISSUE_JSON`
- `GATEWAY_SPEC_PATH`

约定是：agent 只改文件，不直接 push、comment、label 或开 PR；这些副作用由 gateway 统一处理。

## 本地测试

可以保存一个 GitHub issues event payload 到 `/tmp/issue-event.json`，然后直接跑一次：

```bash
export GATEWAY_ALLOW_ANY_REPO=1
export GATEWAY_DRY_RUN=1
python3 scripts/agent_gateway.py --once /tmp/issue-event.json --dry-run
```

也可以测试 HTTP 入口：

```bash
curl -X POST http://127.0.0.1:8787/github/issues \
  -H "Authorization: Bearer $GATEWAY_BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -H "X-GitHub-Event: issues" \
  --data-binary @/tmp/issue-event.json
```

## 常见故障

`Command failed (-9)` 通常表示 agent 子进程被系统杀掉。先检查 job log：

```bash
cat .agent-gateway/jobs/<repo-slug>/<job-id>/gateway.log
cat .agent-gateway/jobs/<repo-slug>/<job-id>/error.txt
```

如果 `/opt/homebrew/bin/codex --version` 报缺少 vendor binary，例如
`@openai/codex-darwin-arm64/.../codex ENOENT`，设置：

```bash
export GATEWAY_CODEX_BIN=/Applications/ChatGPT.app/Contents/Resources/codex
```

然后重启 gateway。

## 安全建议

- 必须设置 `GATEWAY_BEARER_TOKEN`，或者使用真实 GitHub webhook 时设置 `GITHUB_WEBHOOK_SECRET`。
- 必须设置 `GATEWAY_ALLOWED_REPOS`，避免任意 repo 触发本地执行。
- 多 repo 时优先使用 `GATEWAY_REPO_URLS` 或 GitHub payload 自带的 clone URL，不要使用单 repo 的 `GATEWAY_REPO_URL`。
- 本地 agent 使用一次 issue 一个分支：`codex/issue-<number>-spec`。
- 已处理的 issue 会加 `codex:spec-created` label，并写入 `.agent-gateway/state/` 防重复。
- 私有 repo 推荐使用 SSH clone URL，并让本机 runner/gateway 持有部署 key 或 GitHub App token。
