# AGENTS.md — BIBI Design

## 启动仪式

1. 读 SOUL.md — 理解你的设计师身份和排版规范
2. 读 IDENTITY.md — 确认你的角色标识
3. 读取 `/Users/dolan/.openclaw/agents/bibi-agent/data/brief_content.txt`

## 核心职责

收到 bibi-agent 的 spawn 指令后：
1. 读取 `data/brief_content.txt`（bibi-writer 的终稿文本）
2. 按 SOUL.md 设计规范渲染为 HTML
3. 输出到 `docs/daily_brief_YYYY-MM-DD.html`（文件名含当天日期）
4. Git commit + push 到 origin main

## 文件协议

- 读：`/Users/dolan/.openclaw/agents/bibi-agent/data/brief_content.txt`
- 写：`/Users/dolan/.openclaw/agents/bibi-agent/docs/daily_brief_YYYY-MM-DD.html`

## 推送规则

完成 HTML 后：
1. 写入本地 `data/daily_brief_YYYY-MM-DD.html`
2. 通过 GitHub API 推送到 `dolans-brief` 仓库根目录（不是 bibi-intel）
3. GitHub Pages 会自动从 dolans-brief 的 `/` 提供服务

## 沟通规则

完成工作后通过 sessions_spawn 的 announce 机制回报结果给 bibi-agent。
不需要主动联系用户。
