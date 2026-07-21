# Fullsend 项目总结 v2

**生成日期**：2026-07-06  
**读取来源**：`/Users/cc-mini/virtual-space/workspace/fullsend`  
**对照文件**：`/Users/cc-mini/virtual-space/workspace/finding-jobs/Fullsend项目总结.md`

## 1. 一句话结论

Fullsend 已经不只是一个关于 Agentic SDLC 的设计探索文档，而是一个已有 MVP 落地的 GitHub 自动化平台：它通过 GitHub Actions、OpenShell 沙箱、Claude Code 运行时、GCP Workload Identity Federation、中心化 token mint、分角色 GitHub App、默认 agent 套件和安全扫描链，把 issue triage、代码实现、PR review、review fix、retro proposal 等流程串成了可部署、可审计、可扩展的自治软件开发闭环。

当前代码库仍然保留大量 ADR、problem、vision、roadmap 文档，因此它依然是一个持续演进的设计系统；但和最早的总结相比，仓库中已经出现了明确的实现层：Go CLI、复用工作流、composite action、默认 agent harness、post scripts、mint service、admin web、policy/schema/skill/scaffold，以及大量测试和 eval 入口。

## 2. 项目定位与当前状态

### 2.1 项目定位

Fullsend 的目标仍然是探索“全自治 agentic software development lifecycle”：人类设定方向和边界，agent 负责持续把 issue、代码、review、修复、回顾和流程改进推进起来。

它面向 GitHub-hosted organization，核心假设是：

- 人类负责意图、权限边界和最终治理。
- Agent 只在明确授权、受限身份、受限网络、受限文件系统和可审计工作流内运行。
- 自治能力不是一次性打开，而是通过安全证据、质量证据和运营经验逐步获得。
- 所有关键行为要能被复现、追踪、审计和人工介入。

### 2.2 当前状态

从 `docs/roadmap.md` 看，Fullsend 的 Foundation 阶段已完成：

- 2026 年 4 月达到 MVP。
- 2026 年 5 月开始扩大部署。
- 已能安装到 GitHub org 或 repo。
- 已能 enroll repositories。
- 已能运行完整自治 SDLC loop：
  - triage issue；
  - 产出代码和测试；
  - review PR；
  - 根据 review feedback 自动修复；
  - 文件化 retrospective improvement proposals。
- 默认 agent suite 已随项目发布，且设计为可替换、可扩展。
- 文档提到已有 20+ Konflux repositories 在运行 Fullsend。

当前 roadmap 的重点已经从“能不能做”转为“如何让更多项目可靠使用”：

- Adoption and extensibility：让 repo 更容易接入和定制。
- Quality protections：更强的验证、回归防护和人工兜底。
- Agent capabilities：提升默认 agent 能力。
- Versioning and pinning：更清晰地管理 agent、workflow、binary、skill 版本。
- Forge portability：为非 GitHub forge 做准备。
- Feature refinement：补齐产品化细节。

后续方向包括：

- trustworthiness evidence；
- standalone local runtime；
- JIRA-driven workflows；
- auto-merge readiness；
- Kubernetes/OpenShift execution；
- production feedback loops；
- cross-forge orchestration；
- 更强的 security hardening、governance 和 agent attestation。

## 3. 仓库结构要点

当前 `fullsend` 仓库已经明显分成几类内容：

| 区域 | 作用 |
| --- | --- |
| `README.md` | 项目入口，说明 Fullsend 是 living design document 和 reference implementation |
| `docs/` | vision、roadmap、architecture、glossary、problems、plans、guides、ADRs |
| `cmd/fullsend` | 主 CLI 入口 |
| `cmd/mint` | standalone token mint 服务入口 |
| `internal/cli` | `fullsend` CLI 命令实现 |
| `internal/config` | org/repo 配置模型、agent registry、URL pinning、role 配置 |
| `internal/runtime` | agent runtime 抽象和 Claude Code runtime 集成 |
| `internal/harness` | agent harness 解析、组合、校验 |
| `internal/security` | 输入/输出扫描、Unicode 规范化、SSRF、secret redaction、hook、hash chain trace |
| `internal/mintcore` | OIDC token exchange、GitHub App token mint、role permissions、standalone mint core |
| `internal/scaffold/fullsend-repo` | 默认 workflows、agents、harness、policies、schemas、scripts、skills |
| `.github/workflows` | reusable workflows、functional tests、release、deploy 等 CI/CD |
| `action.yml` | Fullsend composite action，用于安装 binary、设置 Podman/OpenShell、运行 `fullsend run` |
| `web/` | public docs/graph 页面和 Svelte admin UI |
| `cloudflare_site/` | Cloudflare Pages/Worker/OAuth 相关配置 |
| `eval/`、`e2e/` | functional eval、行为测试、admin e2e |

## 4. 核心架构

### 4.1 分层执行栈

`docs/architecture.md` 将 Fullsend 执行系统拆成五层：

1. Agent Dispatch and Coordination Layer  
   负责接收事件、选择 agent、编排 stage、触发 workflow。

2. Agent Infrastructure  
   负责 GitHub App、OIDC、token mint、cloud identity、workflow、secret 等基础设施。

3. Agent Sandbox  
   负责隔离执行环境、网络访问、文件系统权限和工具边界。

4. Agent Harness  
   负责把某个 agent 需要的 prompt、schema、policy、script、runtime 参数组合成可执行单元。

5. Agent Runtime  
   负责真正调用底层 coding agent。当前 MVP 主要注册 Claude Code runtime。

关键架构约束是：控制流只能自上而下。下层不能配置上层，sandbox 不能获得不需要的长期凭据，agent 输出必须经过验证和 post-processing，外部副作用由 runner/post-script 承担。

### 4.2 横切组件

架构文档中还有几个横切面：

- Policy Store：保存 sandbox/network/filesystem/tool policy。
- Intent Source：GitHub issue、PR、comment、label、未来的 JIRA 等。
- Identity Provider：GitHub OIDC、GCP WIF、token mint、per-role GitHub Apps。
- Observability：transcript、JSONL telemetry、run summary、trace id、security findings hash chain。
- Agent Registry：配置级 agent 列表，支持 local path 和 URL agent，URL agent 需要 integrity hash pinning。

### 4.3 MVP 的实际落地形态

当前最重要的落地路径是：

1. 目标 repo 中的 shim workflow 接收 GitHub event。
2. shim workflow 调用 Fullsend reusable dispatch workflow。
3. dispatch workflow 根据 event、label、slash command、权限和配置选择 stage。
4. stage workflow 通过 token mint 获取对应 role 的 GitHub App installation token。
5. workflow 准备 `.fullsend` 配置、默认 scaffold、target repo checkout 和 agent 输入。
6. composite action 安装 Fullsend binary、Podman、OpenShell gateway、验证依赖。
7. `fullsend run <agent>` 创建 sandbox，注入必要上下文，运行 agent runtime。
8. agent 输出 JSON、transcript、debug log、metrics。
9. runner 端 post-script 验证输出、执行 secret scan/pre-commit/label/comment/PR 等副作用。
10. artifact、status comment、run summary 和 trace 信息用于后续审计。

## 5. 已实现的主要流程

### 5.1 Per-repo onboarding 流程

当前文档推荐 per-repo 模式。该模式避免一个中心 `.fullsend` repo 管理所有仓库，转而在每个目标 repo 中放置 `.fullsend/config.yaml` 和 shim workflow。

典型流程是：

1. Hosted mint enrollment  
   当前 hosted mint enrollment 文档中仍要求联系 Fullsend team。

2. Provision inference  
   使用 `fullsend inference provision <org>/<repo> --project <gcp-project>` 创建 GCP Workload Identity Federation provider。

3. 安装 agent GitHub Apps  
   每个 role 对应不同 GitHub App 或权限组合，例如 triage、coder、review、retro、prioritize。

4. GitHub setup  
   使用 `fullsend github setup <org>/<repo> --inference-project ... --inference-wif-provider ...` 写入 repo 配置、workflow、variables/secrets。

5. 可选启用指定 agents  
   例如 `--agents triage,review`。

Per-repo 模式下默认 role 包括：

- triage；
- coder；
- review；
- fix；
- retro；
- prioritize。

`fullsend` dispatch role 不再是 per-repo 默认角色。

### 5.2 Per-org onboarding 与维护流程

Per-org 模式仍然存在，但 guide 中已说明计划逐步弱化或废弃，转向 per-repo 模式。

Per-org 模式会创建或维护一个中心 `.fullsend` repo：

- 写入 `.fullsend/config.yaml`；
- 安装 dispatch workflow；
- 维护 enrolled repos；
- 管理 org-level variables/secrets；
- 使用 reusable workflows 调度不同 repo 的 agent runs。

相关命令包括：

- `fullsend github setup <org>`；
- `fullsend github enroll <org> <repo>`；
- `fullsend github unenroll <org> <repo>`；
- `fullsend github status <org>`；
- `fullsend github sync-scaffold <org>`；
- `fullsend github uninstall <org>`。

另外，`fullsend admin install <org-or-owner/repo>` 仍作为 legacy/all-in-one 安装入口存在，可以自动串起 WIF、mint、GitHub setup、per-org/per-repo install 等步骤。较新的文档更强调按职责拆分的 `github`、`inference`、`mint`、`agent` 命令。

### 5.3 GitHub event dispatch 流程

默认 per-repo shim workflow 位于 `internal/scaffold/fullsend-repo/templates/shim-per-repo.yaml`。它监听：

- issue opened/edited/labeled；
- issue_comment；
- pull_request_target opened/synchronize/ready_for_review/closed；
- pull_request_review submitted。

shim 不直接 checkout PR 代码，而是把事件转给 Fullsend reusable dispatch workflow。

`reusable-dispatch.yml` 会根据事件决定 stage：

- issue opened/edited by authorized actor：triage；
- issue label `ready-for-triage`：triage；
- issue label `ready-to-code`：code；
- issue slash command `/fs-triage`、`/fs-code`、`/fs-prioritize` 等：对应 stage；
- PR opened/synchronize/ready_for_review：review；
- PR label `ready-for-review`：review；
- PR review changes_requested by review bot：fix；
- PR closed：retro；
- `/fs-fix`：触发 fix；
- `/fs-retro` 或 `/fullsend retro`：触发 retro。

dispatch 中包含多重保护：

- slash command 需要 write 以上权限；
- 忽略 bot comment；
- 检查 kill switch；
- 检查 role 是否启用；
- fix 阶段阻止 fork PR；
- human-authored PR 需要显式 `fullsend-fix` label 才能自动 fix；
- comment body 做长度限制；
- 使用 concurrency group 避免同一 issue/PR 上重复冲突运行。

### 5.4 Agent runtime 执行流程

主入口是 `fullsend run <agent-name>`。当前 root CLI 中已注册的主要命令包括：

- `agent`；
- `admin`；
- `github`；
- `inference`；
- `lock`；
- `mint`；
- `fetch-skill`；
- `run`；
- `scan`；
- `post-review`；
- `post-comment`；
- `reconcile-status`。

`fullsend run` 的关键步骤包括：

1. 加载 env file 和运行环境。
2. 定位 `.fullsend` 或 scaffold 配置。
3. 自动探测 forge，当前主要为 GitHub。
4. 读取 org/repo config、agent source、harness。
5. 解析 base harness composition。
6. 校验 URL agent、lock file、allowed remote resources。
7. 应用 sandbox image、files、env、runtime hooks。
8. 如果配置了 role 和 mint URL，则为 agent mint scoped token。
9. 校验 script 权限并 lint harness。
10. 创建或更新 status comment。
11. 检查 OpenShell gateway 和 provider。
12. 解析 trace identity。
13. 运行 pre-script。
14. 创建 sandbox。
15. 配置 telemetry、transcript、runtime fetch service。
16. 注入 Fullsend binary、env、runtime hooks。
17. 将 target repo copy 进 sandbox。
18. 注入 org-level `AGENTS.md` 和 `CLAUDE.md` pointer。
19. 扫描上下文文件。
20. 注入 trace id。
21. 运行 pre-agent security scan。
22. 在 sandbox 内做 GitHub API preflight。
23. 运行 agent loop 和 validation iteration。
24. 抽取 output、transcripts、debug log。
25. 安全下载 target repo，清理危险 symlink 和 `.git/hooks`。
26. 运行 validation script。
27. 写 metrics。
28. surfacing transcript errors。
29. 运行 post-agent output scan。
30. 校验 security findings hash chain。
31. 成功时再运行 post-script。

`fullsend run` 默认会把副作用推迟到 post-script 阶段，因此 agent 自身通常不能直接 push、comment、merge、label 或改 issue。

### 5.5 Composite action 流程

`action.yml` 是 Fullsend 的 GitHub composite action。它负责：

- 安装 fullsend binary，来源可以是 vendored binary、release 或 source build；
- 安装 Podman；
- 配置 OpenShell gateway；
- 安装验证依赖；
- 如果 target repo 有 `go.mod`，安装 Go；
- 调用 `fullsend run`；
- finalize orphan status comments；
- 上传 artifacts。

它刻意不暴露 `--no-post-script`，因为在 GitHub workflow 中跳过 post-script 会破坏平台的副作用边界和审计假设。

## 6. 默认 agent 套件

当前 scaffold 中已经包含一套默认 agent：

| Agent | 主要作用 | 关键输出 |
| --- | --- | --- |
| triage | 分析 issue 是否清晰、是否重复、是否有前置依赖、是否 ready-to-code | `triage-result.json` |
| prioritize | 对 issue 做 RICE 评分并写入项目管理上下文 | `prioritize-result.json` |
| code | 根据 ready issue 实现最小代码变更和测试 | `code-result.json` |
| review | 对 PR 做多维审查，输出 approve/comment/request-changes/reject/failure | `review-result.json` |
| fix | 根据 review feedback 或人工 `/fs-fix` 修复 PR | `fix-result.json` |
| retro | 在 PR closed 后总结流程问题，提出改进 proposal | `retro-result.json` |

### 6.1 Triage agent

Triage agent 会读取 issue、repo context、历史 triage、重复 issue、前置依赖等信息。它可以输出：

- `question`；
- `insufficient`；
- `duplicate`；
- `sufficient`；
- `prerequisites`。

只有当信息缺口关闭、实现路径足够清晰时，才会把 issue 推向 ready-to-code。

Post-script 会：

- 使用 labels API 更新标签，避免 `issues.edited` 触发循环；
- 对 duplicate 关闭 issue；
- 对 prerequisites 创建允许范围内的前置 issue；
- 对 sufficient 的 bug/documentation/performance 添加 `ready-to-code`；
- 对 feature 标记 feature/triaged；
- 使用 sticky comment 汇总结果。

### 6.2 Code agent

Code agent 是实现专家。它被要求：

- 验证 root cause；
- 做最小必要改动；
- 补测试；
- 不直接 push、创建 PR、merge、comment 或编辑 issue；
- 不绕过平台边界。

`post-code.sh` 在 runner 端处理副作用：

- 读取 `code-result.json` 中的 target branch；
- 校验 branch allowlist/default branch；
- 如果无改动则 no-op；
- 删除 agent artifact dirs；
- 运行固定版本和 hash 的 gitleaks；
- 拒绝 Signed-off-by 等不期望内容；
- 根据 `.pre-commit-tools.yaml` 安装并运行 authoritative pre-commit；
- 对 auto-fix 后结果再次 secret scan；
- push branch，必要时处理 stale remote branch；
- 创建 PR；
- 注入 issue 编号、PR body checklist 和 ready-for-review label。

### 6.3 Review agent

Review agent 是 PR 审查编排器。它可以使用 subagents 从 correctness、security、intent、style、docs、cross-repo contract 等角度检查 PR。

它的关键约束是：

- PR 元数据通过 GitHub API 获取；
- 默认 zero trust；
- label action 必须通过 schema 和 post-script 过滤；
- 高风险或 protected paths 不能直接自动 approve；
- 输出必须符合 `review-result.schema.json`。

`post-review.sh` 会：

- 拒绝 closed/merged PR；
- 找到最新 agent result；
- 执行 severity threshold；
- 如果 approve 但 PR 触及 `.github/`、CODEOWNERS、agents、harness、policies、scripts、skills、Dockerfile 等 protected paths，则降级为 comment 并追加人工 review 提醒；
- 只允许应用已有标签，且拒绝控制标签；
- 调用 `fullsend post-review`；
- 若发现 stale head，会发 `/fs-review` marker 触发重跑；
- 对 approve 添加 ready-for-merge；
- 对 downgraded/comment 添加 requires-manual-review；
- 对 reject 关闭 PR 并标记 rejected。

### 6.4 Fix agent

Fix agent 用于处理 review feedback 或人工 `/fs-fix`。默认复用 coder role，因此权限模型上和 code agent 接近，但输入来自 PR review 或人工指令。

Fix workflow 会：

- 阻止 fork PR；
- 提取 PR context、review body、fix instruction、iteration；
- 检查是否允许 fix；
- checkout PR HEAD；
- 将 review body 限制在 1MB 内；
- 运行 fix agent。

`post-fix.sh` 会：

- 读取并校验 `fix-result.json`；
- secret scan；
- Signed-off-by 检查；
- pre-commit；
- push 修复；
- 在接近 bot iteration cap 时标记 needs-human；
- 评论修复总结。

### 6.5 Retro agent

Retro agent 是 read-only analyst。它不直接改代码，而是在 PR closed 后分析本次 agent run 暴露的问题，并通过 post-script 创建改进 issue。

它关注：

- agent scaffolding；
- autonomy readiness；
- repeated failure modes；
- missing guardrails；
- process improvement proposals。

`post-retro.sh` 会校验 proposals、创建改进 issue、创建需要的标签，并在权限不足时优雅处理 comment 失败。

### 6.6 Prioritize agent

Prioritize agent 使用 RICE 模型：

- Reach；
- Impact；
- Confidence；
- Effort。

它可把优先级评分写回 GitHub Project 字段或 comment，用于 backlog 排序。

## 7. Token mint 与身份模型

Fullsend 的身份核心是：agent 不直接持有长期 PAT，也不把高权限凭据放进 sandbox。GitHub Actions 使用 OIDC 获取短期身份，向 token mint 请求特定 role、特定 repo 范围的 GitHub App installation token。

### 7.1 Mint 流程

典型流程：

1. GitHub Actions job 请求 OIDC token。
2. Workflow 调用 mint endpoint：`POST /v1/token`。
3. 请求中包含 role 和 repos。
4. Mint 校验 OIDC issuer、audience、repository owner、workflow provenance。
5. Mint 根据 role 找到对应 GitHub App。
6. Mint 从 Secret Manager 或本地 PEM dir 加载私钥。
7. Mint 生成 GitHub App JWT。
8. Mint 查找 installation。
9. Mint 创建 scoped installation token。
10. Workflow 只把这个短期 token 用在对应 stage。

### 7.2 Role 与权限

代码和文档中出现的 role 包括：

- fullsend；
- triage；
- coder；
- review；
- fix；
- retro；
- prioritize；
- e2e。

实际配置里 fix 常常复用 coder app/role。Mint core 会校验 role、allowed roles、repo 名称、repo 数量上限、target org、same-org 或 cross-org allowlist。

### 7.3 Hosted、tight、public、standalone mint

Mint 支持多种部署/校验模式：

- Tight mint：限制 org、workflow ref、registered per-repo WIF repos。
- Public mint：`ALLOWED_ORGS=*` 时，只允许来自 Fullsend 上游 public workflows 的请求。
- Standalone mint：`cmd/mint` 提供本地 HTTP 服务，使用 JWKS verifier，不依赖 GCP STS/WIF。
- Fallback mint：standalone mint 可配置 fallback URL。

相关 CLI 包括：

- `fullsend mint deploy`；
- `fullsend mint enroll`；
- `fullsend mint unenroll`；
- `fullsend mint status`；
- `fullsend mint token`；
- `fullsend mint add-role`；
- `fullsend mint remove-role`。

## 8. 安全模型与已实现防护

Fullsend 的安全实现比早期设计更具体，已经出现在 CLI、runtime hook、sandbox policy、post-script 和 mint 中。

### 8.1 输入/输出扫描

`internal/security` 中实现了输入和输出扫描 pipeline：

- UnicodeNormalizer；
- ContextInjectionScanner；
- SecretRedactor。

Unicode normalizer 会处理：

- null bytes；
- ANSI/OSC escape；
- zero-width characters；
- bidi override；
- tag characters；
- variation selectors；
- Unicode format characters；
- NFKC normalization；
- normalize 后再次逃逸控制字符。

Context injection scanner 会扫描：

- `AGENTS.md`；
- `CLAUDE.md`；
- `.cursorrules`；
- `skill.md`；
- `plugin.json`；
- 其他 prompt/context 文件。

它会识别 instruction override、credential exfiltration、hidden comments/divs、translate-and-execute 等模式。

### 8.2 `fullsend scan`

CLI 已有 `fullsend scan` 命令：

- `fullsend scan input`；
- `fullsend scan output`；
- `fullsend scan context`；
- `fullsend scan url`。

输入扫描可对 GitHub event payload 做 Unicode、injection、SSRF 等检查。输出扫描会做 secret redaction。Context 扫描会检查已知上下文文件。

### 8.3 Runtime hooks

Claude settings 中注入了多种 hook：

- PreToolUse Bash hook：Tirith，默认启用；
- PreToolUse Bash/WebFetch hook：SSRF；
- PreToolUse all tools：canary；
- 可选 tool allowlist；
- PostToolUse Bash/WebFetch/Read：context suppress、unicode normalize、secret redact；
- PostToolUse all tools：canary。

Hook 顺序有明确约束：Unicode 处理必须在 secret redaction 之前。

### 8.4 Sandbox policy

默认 policy 使用 OpenShell 风格的隔离：

- filesystem include workdir；
- 系统目录 read-only；
- `/sandbox` 和 `/tmp` read-write；
- run as non-root sandbox user；
- L7 endpoint restrictions；
- binary-level restrictions。

不同 agent 的网络权限不同：

- code/fix 需要 GitHub API、Vertex AI、package registries、gitleaks 等；
- review/retro 更偏 read-only；
- triage/prioritize 主要需要 GitHub 和 Vertex。

部分 policy 故意不允许 curl，避免绕过更细粒度工具边界。

### 8.5 Runner 端安全后处理

关键副作用不在 sandbox 内完成，而在 runner post-script 中完成：

- gitleaks；
- pre-commit；
- Signed-off-by 检查；
- protected path downgrade；
- label allowlist；
- branch allowlist；
- stale PR head 重试；
- fork PR fix 阻断；
- artifact 清理；
- secret scan 后再 push/comment。

### 8.6 Security findings hash chain

`internal/security/trace.go` 中实现了 hash-chained JSONL findings。每条 finding 带 `prev_hash` 和 `hash`。`fullsend run` 会校验 findings chain，检测删除或篡改。

## 9. 配置、agent registry 与可扩展性

### 9.1 配置模型

`internal/config` 中的配置版本为 `version: 1`。核心字段包括：

- dispatch platform 和 mode；
- inference provider；
- defaults；
- roles；
- repos；
- agents；
- allowed remote resources；
- create issues policy。

默认 dispatch mode 是 OIDC mint。默认 inference provider 是 Vertex。

### 9.2 Agent registry

Fullsend 支持配置级 agent registry：

- local path agent；
- URL agent；
- URL agent 自动 pin `sha256`；
- URL agent 必须匹配 `allowed_remote_resources`；
- local path 不能使用 absolute path、反斜杠或 `..`。

相关命令包括：

- `fullsend agent add`；
- `fullsend agent list`；
- `fullsend agent update`；
- `fullsend agent remove`。

这说明 Fullsend 已经从“内置 agent 套件”扩展到“可替换 agent distribution”。

### 9.3 Harness、policy、schema 分离

每个 agent 的执行单元由 harness 声明，通常包括：

- agent prompt；
- model；
- sandbox image；
- policy；
- role；
- host files；
- skills；
- plugins；
- pre-script；
- post-script；
- validation loop；
- output schema；
- timeout；
- runner-only env。

这种拆法让 agent 行为、权限和后处理边界都可以独立演进。

## 10. Observability 与审计

当前实现中的可观测性包括：

- JSONL transcripts；
- `run-telemetry.jsonl`；
- `run-summary.json`；
- trace id；
- status comment；
- uploaded artifacts；
- debug log；
- security findings hash chain；
- transcript error surfacing；
- workflow artifacts；
- post-script summary comment。

Roadmap 和 architecture 还提到 distributed tracing 和更强 trustworthiness evidence，说明 observability 仍在继续产品化。

## 11. Web、Admin 与站点

仓库中已有多种 web surface：

- `web/public`：公开页面、graph/document browser；
- `web/admin`：Svelte admin UI，包含 auth、layers、org list、status engine 等模块；
- `cloudflare_site`：Cloudflare Pages/Worker/OAuth 配置；
- `website`：文档或站点相关内容。

目前 CLI 和 GitHub workflows 仍是主干路径，但 admin web 已经出现，用于安装状态、层级状态和运营可视化的基础能力。

## 12. 测试与验证

仓库已有多层测试和验证入口：

- Go unit tests 分布在 `internal/*`；
- shell/Python scripts 测试；
- workflow functional tests；
- `eval/triage` functional eval；
- `e2e/admin` 与 `e2e/behaviour`；
- web admin TypeScript/Vitest/Playwright 相关测试入口；
- reusable workflows 自身的验证逻辑；
- post-script 的 schema、secret、pre-commit、branch、label、protected path 检查。

这说明项目已经在补齐从单元级、脚本级、workflow 级到行为级的回归防线。

## 13. 当前实现状态矩阵

| 能力 | 当前状态 | 说明 |
| --- | --- | --- |
| GitHub org/repo setup | 已实现 | `fullsend github setup/status/enroll/unenroll/uninstall/sync-scaffold` |
| Per-repo mode | 已实现且推荐 | docs 中明确 per-org 未来弱化 |
| Per-org mode | 已实现但趋向 legacy | 中心 `.fullsend` repo 仍可用 |
| All-in-one admin install | 已实现但偏 legacy | `fullsend admin install` |
| Agent runtime | 已实现 | `fullsend run`，当前 MVP 主要是 Claude Code runtime |
| Default agents | 已实现 | triage、prioritize、code、review、fix、retro |
| Token mint | 已实现 | GCP Cloud Function/standalone mint，共用 `mintcore` |
| Per-role GitHub Apps | 已实现 | role app mapping、scoped installation token |
| Security scans | 已实现 | input/output/context/url scan、Unicode、injection、secret redaction |
| Runtime hooks | 已实现 | Claude PreToolUse/PostToolUse hooks |
| Sandbox policy | 已实现 | OpenShell、filesystem/network/tool restrictions |
| Post-script guardrails | 已实现 | gitleaks、pre-commit、protected path、label/branch checks |
| Agent registry | 已实现 | local/URL agent、sha256 pinning、allowed remote resources |
| Lock/version pinning | 部分实现 | lock command 和 URL integrity 已有，roadmap 仍继续推进 |
| Observability | 部分到已实现 | transcripts、telemetry、summary、trace 已有，更强 evidence 仍在推进 |
| Admin web | 部分实现 | Svelte admin UI 和 Cloudflare/OAuth surface 已存在 |
| JIRA workflow | 规划/部分设计 | roadmap/ADR 中出现，root CLI 中未见完整用户入口 |
| `fullsend repos` | 规划/部分代码 | `internal/repos` 存在，但 root CLI 当前未注册 `repos` 命令 |
| Auto-merge | 未来方向 | roadmap 中仍是 next/later readiness |
| Kubernetes/OpenShift execution | 未来方向 | roadmap later |

## 14. 与最开始《Fullsend项目总结.md》的主要区别

### 14.1 项目阶段不同

旧版总结把 Fullsend 描述为 Phase 1 的“发散探索”和 living design document。新版读取到的仓库显示 Foundation 已完成，项目已经达到 MVP，并在多个 Konflux repositories 中运行。

变化：

- 旧版：以问题定义、威胁模型、原则和路线图为主。
- 新版：已有可安装、可运行、可审计的 reference implementation。

### 14.2 Roadmap 表达不同

旧版采用 Phase 1 到 Phase 5 的阶段式路线：

- Phase 1：发散探索；
- Phase 2：收敛原则；
- Phase 3：最小安全原型；
- Phase 4：受控试点；
- Phase 5：平台化扩展。

新版 roadmap 已改为：

- Foundation done；
- Now；
- Next；
- Later。

当前重点也从“探索可行性”转为“采用、扩展、质量保护、版本 pinning、forge portability、auto-merge readiness 和 trust evidence”。

### 14.3 架构从概念变成执行系统

旧版总结中的架构多是原则性描述：security foundation、autonomy earned、human direction、transparency、start anywhere。

新版中已经有实际执行栈：

- dispatch；
- infrastructure；
- sandbox；
- harness；
- runtime。

并且已有 GitHub Actions、OpenShell、Claude Code、GCP WIF、token mint、post-script、schema validation 等具体实现。

### 14.4 安装模型发生变化

旧版更像围绕中心 `.fullsend` repo 和 org-level 安装来描述。

新版中 per-repo mode 已成为推荐路径：

- 每个 repo 有自己的 `.fullsend/config.yaml`；
- 每个 repo 有 shim workflow；
- per-org mode 仍可用，但文档中已标为未来弱化方向。

这说明 Fullsend 在部署模型上从“中心化管理”向“repo-local、低摩擦接入”移动。

### 14.5 默认 agent 套件已经落地

旧版更多讨论可能需要哪些 agent 和 agentic SDLC 的职责拆分。

新版仓库中已有默认 agent：

- triage；
- prioritize；
- code；
- review；
- fix；
- retro。

并且每个 agent 都有 prompt、harness、policy、schema、skills 和 post-script 配套。

### 14.6 Review/Fix/Retro 闭环更完整

旧版已经强调 code review 和 feedback loop 的重要性，但更多是问题和方向。

新版中实际流程已经能做到：

- issue triage；
- code PR；
- PR review；
- review changes_requested 自动触发 fix；
- PR closed 后触发 retro；
- retro 产生改进 proposal issue。

这已经形成从 intent 到改进反馈的自治循环。

### 14.7 身份和权限模型更具体

旧版提到 per-role GitHub Apps、OIDC、最小权限等安全设计。

新版中已经有：

- `internal/mintcore`；
- `cmd/mint`；
- GCP Cloud Function mint；
- standalone mint；
- `/v1/token`；
- role app mapping；
- workflow provenance 校验；
- same-org/cross-org allowlist；
- custom role permissions；
- fallback mint。

也就是说身份模型已经从原则推进到可运行服务。

### 14.8 安全防护从威胁模型变成代码路径

旧版大量讨论 prompt injection、credential exfiltration、untrusted code、network boundary、human trust 等威胁。

新版中已有对应实现：

- Unicode normalizer；
- context injection scanner；
- SSRF scanner；
- secret redactor；
- Claude runtime hooks；
- OpenShell policy；
- binary-level network restrictions；
- sandbox safe download；
- `.git/hooks` 清理；
- gitleaks；
- pre-commit；
- protected path approve downgrade；
- label/branch allowlist；
- findings hash chain。

### 14.9 Agent extensibility 更成熟

旧版主要讲“要能扩展 agent、skill、workflow”。

新版已经实现：

- `agents:` config；
- local path agent；
- URL agent；
- URL sha256 pinning；
- allowed remote resources；
- `fullsend agent add/list/update/remove`；
- harness base composition；
- lock/version pinning 的部分能力。

### 14.10 Observability 更具体

旧版强调 transparency 和 auditability。

新版已经出现具体产物：

- JSONL transcripts；
- run telemetry；
- run summary；
- debug log；
- trace id；
- status comments；
- workflow artifacts；
- security findings hash chain；
- transcript error surfacing。

### 14.11 CLI surface 更大

旧版没有完整 CLI 命令面。

新版 root CLI 中已有：

- `agent`；
- `admin`；
- `github`；
- `inference`；
- `lock`；
- `mint`；
- `fetch-skill`；
- `run`；
- `scan`；
- `post-review`；
- `post-comment`；
- `reconcile-status`。

不过也要注意：architecture/ADR/docs 中出现的一些概念，例如 `fullsend repos`、CEL dispatch、polling/JIRA 等，在当前 root CLI 中还没有完整显式命令入口，应视为规划、局部实现或正在演进的能力。

### 14.12 Web/Admin surface 是新版新增重点

旧版总结主要关注 docs、CLI、Actions 和架构。

新版仓库中已经有：

- public web；
- graph page；
- Svelte admin UI；
- Cloudflare Worker/OAuth；
- admin status engine。

这表明项目正在从纯 CLI/Actions reference implementation 走向可运营的平台界面。

### 14.13 测试和 eval 更完整

旧版只宏观提到测试、Playwright、e2e 等方向。

新版仓库中可见：

- Go tests；
- script tests；
- functional workflow tests；
- triage eval；
- admin e2e；
- behaviour e2e；
- web/admin 测试入口；
- post-script 多重验证。

质量防线已经更像真实平台。

## 15. 需要留意的边界和未完全落地项

虽然当前实现已经很完整，但仍有一些需要区分“设计已确定”和“用户可直接使用”的地方：

- `docs/architecture.md` 和 ADR 中描述的部分 dispatch/poll/CEL/JIRA 能力，不一定都有当前 root CLI 命令入口。
- `internal/repos` 存在，但 root CLI 当前没有注册 `fullsend repos`。
- Per-org 模式仍可用，但文档趋势是推荐 per-repo。
- Auto-merge 仍是 readiness 方向，不是默认闭环。
- Kubernetes/OpenShift execution 仍是 later roadmap。
- Admin web 已有代码，但 CLI/GitHub Actions 仍是主要生产路径。
- Lock/version pinning 已有基础能力，但 roadmap 仍把 versioning and pinning 作为当前重点。

## 16. 总结判断

和最早的总结相比，Fullsend 已经从“关于自治 SDLC 的系统性问题研究”推进为“可运行的自治开发平台原型”。它最有价值的进展不是某一个 agent，而是把多个边界同时打通：

- GitHub event 到 agent run；
- OIDC 到 per-role GitHub App token；
- sandbox 内分析/生成到 runner 端安全副作用；
- prompt/harness/policy/schema/post-script 分层；
- triage/code/review/fix/retro/prioritize 默认闭环；
- 安全扫描、runtime hooks、network policy 和 hash-chain audit；
- repo-local 配置、agent registry、URL pinning 和可扩展 scaffold。

旧版总结仍适合作为 Fullsend 思想源头和问题空间地图；新版 v2 更应该被看作当前实现状态、可用流程和工程边界的快照。
