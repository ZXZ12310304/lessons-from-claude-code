# Lessons from Claude Code

基于claude代码提取的面向工程师的 Coding Agent 架构拆解与复建手册（中英双语）。

- 在线阅读: https://lessons-from-claude-code.netlify.app/
- 内容来源: `contents/` Markdown 自动生成到 `html-site/`
- 默认入口: English，支持中英文切换

## 项目定位

这个项目重点是提炼可复用的工程模式：

- Query Loop 与会话生命周期
- 工具体系（契约、调度、执行）
- 权限与安全边界
- 上下文预算与压缩策略
- 多 Agent 协作与工程化落地

## 内容导航

- `Map`: 阅读路径、术语、证据规范
- `Mechanism`: 系统如何运转
- `Decision`: 为什么这样设计
- `Build`: 如何最小实现并稳定上线

## 快速开始

### 1) 本地查看静态站点

直接打开：`html-site/index.html`

### 2) 从 Markdown 重新构建站点

```bash
python scripts/build_site.py
```

构建后产物在：`html-site/`

## 仓库结构

```text
contents/              # 文章源文件（zh + en）
scripts/build_site.py  # 站点生成脚本
html-site/             # 静态站点产物（可直接部署）
claude-code-main/      # 代码锚点参考快照
```

## 写作与编辑约定

- 每篇文章都给出明确代码锚点（`path + symbols`）
- 区分事实、跨文件证据和推断
- 优先解释机制与权衡，而不是实现细枝末节
- 中文与英文内容保持可对齐的结构

## 适合谁

- 在做 Coding Agent / AI IDE / Agent Runtime 的工程师
- 需要落地权限治理、工具编排、上下文治理的团队
- 希望把“能跑 demo”升级到“可持续运行系统”的开发者

## 贡献方式

欢迎通过 Issue / PR 提交：

- 纠错与补充证据
- 新文章提案（机制 / 决策 / 复建）
- 构建脚本和站点体验改进
