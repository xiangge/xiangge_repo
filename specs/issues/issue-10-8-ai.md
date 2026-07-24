# Issue 10: 本周前 8 条最新 AI 新闻总结

## Summary

为关注 AI 实时动态的读者整理本周最新的 8 条 AI 新闻。最终产物需要包含一份 Markdown 新闻简报和对应 PDF 文件，分别放入新建的 `ai-news-md` 与 `ai-news-pdf` 文件夹。

本 issue 来自 GitHub Issue #10，创建时间为 2026-07-24。实现时应以执行当天所在自然周为准，并优先选取本周内发生或发布的 AI 领域重要新闻。

## Goals

- 收集本周最新、重要、可信的 8 条 AI 新闻。
- 面向关注 AI 实时动态的读者，用中文总结每条新闻的核心事实、影响和关注点。
- 新建 `ai-news-md` 文件夹，并在其中生成 Markdown 格式新闻简报。
- 新建 `ai-news-pdf` 文件夹，并将 Markdown 简报转换为 PDF 后放入该文件夹。
- 保留新闻来源链接、发布日期或事件日期，便于读者核验。
- 后续提交的 commit message 需要体现 `Assisted-by: AI-SDLC`。

## Non-Goals

- 不生成长期新闻站点、自动订阅系统或爬虫服务。
- 不对新闻进行投资、法律、医疗或政策合规建议。
- 不需要覆盖所有 AI 新闻，只需选取本周最值得关注的 8 条。
- 当前 requirements spec 任务不执行 commit、push、建分支、创建 PR、添加 label 或评论 GitHub；这些 side effects 由 issue gateway 处理。

## User Stories And Acceptance Criteria

### User Stories

- 作为关注 AI 实时动态的读者，我希望快速看到本周最重要的 8 条 AI 新闻，以便了解行业最新进展。
- 作为读者，我希望每条新闻都有来源和日期，方便继续阅读原文或核实信息。
- 作为仓库维护者，我希望新闻简报同时提供 Markdown 与 PDF，便于在仓库中查看和分发。

### Acceptance Criteria

- 仓库中存在 `ai-news-md` 文件夹。
- 仓库中存在 `ai-news-pdf` 文件夹。
- `ai-news-md` 中至少包含 1 个 `.md` 新闻简报文件。
- `ai-news-pdf` 中至少包含 1 个与 Markdown 简报对应的 `.pdf` 文件。
- Markdown 简报包含标题、生成日期、本周时间范围、8 条新闻条目和来源列表或逐条来源链接。
- 每条新闻包含：
  - 新闻标题；
  - 发布日期或事件日期；
  - 来源名称与链接；
  - 2 到 4 句中文摘要；
  - 对 AI 关注者的简短影响分析。
- 新闻条目必须为本周内最新内容；若来源发布时间与事件发生时间不同，应在文中明确说明。
- PDF 内容应与 Markdown 主体一致，排版可读，无明显乱码、截断或空白页。
- 后续提交信息中应包含 `Assisted-by: AI-SDLC`。

## Implementation Notes

- 由于新闻具有时效性，实现时必须联网核验最新来源，不能仅依赖模型记忆。
- 优先使用权威或一手来源，例如公司官方博客、研究机构公告、监管机构公告、主流科技媒体或论文/模型发布页。
- 建议按执行日期确定本周范围；若按 Issue 创建日期计算，本周可理解为 2026-07-20 至 2026-07-26 这一自然周。
- Markdown 文件建议命名为 `ai-news-YYYY-MM-DD.md`，PDF 文件建议使用相同 basename，例如 `ai-news-YYYY-MM-DD.pdf`。
- Markdown 建议结构：
  - 标题与生成日期；
  - 本周时间范围；
  - 8 条编号新闻；
  - 总结或趋势观察；
  - 来源链接。
- PDF 转换可使用仓库现有工具、Pandoc、Markdown 渲染库，或其他稳定的本地转换方式；需确保中文字体渲染正常。
- 如果无法安装额外依赖，应优先使用当前环境已有工具完成转换，并在最终说明中记录限制。
- 执行 GitHub side effects 时应遵守 gateway 约束；本 spec 创建任务本身不得 commit、push、建分支或创建 PR。

## Validation Plan

- 检查 `ai-news-md` 与 `ai-news-pdf` 两个目录存在。
- 检查 Markdown 文件存在且包含 8 条新闻，不多不少。
- 抽查每条新闻链接可访问，日期属于本周或明确说明事件发生于本周。
- 检查 Markdown 中的中文内容、标题层级和链接格式正确。
- 打开或渲染 PDF，确认页数合理、中文无乱码、内容无明显缺失。
- 对比 Markdown 与 PDF，确认 8 条新闻标题和主要摘要一致。
- 运行 `git status --short`，确认只有预期新增或修改文件。

## Open Questions

- “前 8 条”应按发布时间倒序选取，还是按重要性排序后选取 8 条？
- “这周”应按执行环境时区、Issue 创建时间所在时区，还是读者所在地时区计算？
- PDF 是否需要特定版式、封面或文件命名规范？
- 是否允许引用英文来源并提供中文总结，还是必须优先中文来源？
