# AI Config — Portable Agent Instructions

本目录存放通用的 AI agent 指令文件，可迁移到不同工具。核心文件 `AI_INSTRUCTIONS.md` 合并了 CLAUDE.md 和 memory 中的所有身份、偏好与框架信息，是唯一的跨平台配置文件。

---

## 文件说明

| 文件 | 用途 |
|------|------|
| `AI_INSTRUCTIONS.md` | 通用指令文件，作为所有 agent 的 system prompt prefix |

---

## 迁移到各 Agent — 具体步骤

### Claude Code（已配置）

当前目录已通过以下文件生效，无需额外操作：
- `../CLAUDE.md` — 项目指令
- `~/.claude/projects/.../memory/` — 持久化记忆

如需在其他目录使用，复制 `AI_INSTRUCTIONS.md` 内容到目标目录的 `CLAUDE.md` 即可。

---

### Codex (OpenAI)

**方式一：项目级配置**
```bash
cp AI_INSTRUCTIONS.md /path/to/your-project/CODEX.md
```
Codex 在项目根目录检测到 `CODEX.md` 后自动加载。

**方式二：全局用户配置**
```bash
mkdir -p ~/.codex
cp AI_INSTRUCTIONS.md ~/.codex/instructions.md
```
全局生效，所有 Codex session 均会加载。

**方式三：Session 内手动加载**
在 Codex 对话中输入：
```
/load AI_INSTRUCTIONS.md
```

---

### Gemini CLI (Google)

**项目级配置：**
```bash
cp AI_INSTRUCTIONS.md /path/to/your-project/GEMINI.md
```

**全局配置：**
```bash
cp AI_INSTRUCTIONS.md ~/.gemini/GEMINI.md
```

Gemini CLI 启动时自动检测并加载 `GEMINI.md`。也可在对话中用 `/load` 手动加载。

---

### Cursor

**项目级配置：**
```bash
cp AI_INSTRUCTIONS.md /path/to/your-project/.cursorrules
```

**全局配置：**
在 Cursor 中打开 Settings → Rules → Add Rule → 粘贴 `AI_INSTRUCTIONS.md` 内容。

Cursor 支持 `.cursorrules` 文件，也支持更细粒度的 `.cursor/rules/` 目录。对于简单场景，`.cursorrules` 足够。

---

### GitHub Copilot

**项目级：**
```bash
mkdir -p /path/to/your-project/.github
cp AI_INSTRUCTIONS.md /path/to/your-project/.github/copilot-instructions.md
```

**Workspace 级（VSCode）：**
在 VSCode 设置中搜索 `github.copilot.chat.codeGeneration.instructions`，将 `AI_INSTRUCTIONS.md` 内容粘贴到对应工作区设置。

**全局：**
VSCode 设置 → `github.copilot.chat.codeGeneration.instructions` → 粘贴内容到 User Settings。

---

### Windsurf

**项目级：**
```bash
cp AI_INSTRUCTIONS.md /path/to/your-project/.windsurfrules
```

**全局：**
```bash
mkdir -p ~/.windsurf
cp AI_INSTRUCTIONS.md ~/.windsurf/rules.md
```

Windsurf 同时支持 `.windsurfrules`（项目）和 `~/.windsurf/rules.md`（全局），两者可并存，项目级优先级更高。

---

### Cline (VSCode Extension)

在 VSCode 中打开 Cline 设置 → `System Prompt` → 追加 `AI_INSTRUCTIONS.md` 内容到 Custom Instructions 字段。

---

### Aider

**项目级：**
```bash
cp AI_INSTRUCTIONS.md /path/to/your-project/.aider.conf.md
```

**全局：**
```bash
cp AI_INSTRUCTIONS.md ~/.aider.conf.md
```

Aider 将 `.aider.conf.md` 的内容注入到每次对话的 system prompt 中。

---

### Tray / 通用 Agent 平台

大多数 agent 平台（Tray、LangChain、CrewAI 等）支持直接设置 System Prompt：

1. 找到 Agent 配置中的 **System Prompt** 或 **Instructions** 字段
2. 将 `AI_INSTRUCTIONS.md` 全文粘贴进去
3. 确保在 User Prompt 之前注入

示例（Python SDK 伪代码）：
```python
agent = Agent(
    system_prompt=open("AI_INSTRUCTIONS.md").read(),
    model="claude-sonnet-4-6"
)
```

---

### 通用 Chat UI

**ChatGPT:**
Settings → Personalization → Custom Instructions → 将 `AI_INSTRUCTIONS.md` 内容粘贴到 "What would you like ChatGPT to know about you?" 字段。

**Claude.ai (Web):**
Settings → Profile → Custom Instructions → 粘贴 `AI_INSTRUCTIONS.md` 内容。

**DeepSeek Chat:**
设置 → System Prompt → 粘贴内容。

---

## 同步与维护

```
单一真相来源: AI_INSTRUCTIONS.md
                    │
     ┌──────────────┼──────────────┐
     ▼              ▼              ▼
  CLAUDE.md     memory/*.md    其他 agent 的 Instructions
  (框架&格式)    (身份&偏好)    (直接复制)
```

**维护规则：**

1. **修改身份/偏好/框架时** → 先改 `AI_INSTRUCTIONS.md`，再同步到 CLAUDE.md 或对应 memory 文件
2. **Claude Code 中通过对话新增记忆时** → 手动将关键内容同步回 `AI_INSTRUCTIONS.md`
3. **迁移到新 agent 时** → 从 `AI_INSTRUCTIONS.md` 复制，不要从各 agent 的本地文件反向导出

---

## 版本控制

建议将 `ai-config/` 纳入 Git 私有仓库管理：

```bash
cd /path/to/workspace
git init
git add ai-config/
git commit -m "Add portable AI agent instructions"
```

不要将 `~/.claude/projects/` 路径下的 memory 文件直接纳入版本控制（路径含特殊字符，且包含 session 元数据）。始终以 `AI_INSTRUCTIONS.md` 为版本化的唯一配置源。
