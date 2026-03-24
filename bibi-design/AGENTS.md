# AGENTS.md — BIBI Design

## 启动仪式

1. 读 SOUL.md — 理解你的设计师身份和排版规范（必须严格遵守）
2. 读 IDENTITY.md — 确认你的角色标识
3. 读取 `/Users/dolan/.openclaw/agents/bibi-agent/data/brief_content.txt`

## 核心职责

收到 bibi-agent 的 spawn 指令后：
1. 读取 `data/brief_content.txt`（bibi-writer 的终稿文本）
2. 按 SOUL.md 设计规范渲染为 HTML（**禁止擅自变更设计风格**）
3. 输出到 `data/daily_brief_YYYY-MM-DD.html`（文件名含当天日期）
4. 同步复制到 `docs/daily_brief_YYYY-MM-DD.html`
5. Git add + commit + push 到 origin main

## 文件协议（强制）

- 读：`/Users/dolan/.openclaw/agents/bibi-agent/data/brief_content.txt`
- 写：`/Users/dolan/.openclaw/agents/bibi-agent/data/daily_brief_YYYY-MM-DD.html`
- 复制：`/Users/dolan/.openclaw/agents/bibi-agent/docs/daily_brief_YYYY-MM-DD.html`

## 推送规则（强制）

**GitHub 仓库：必须是 `bibi-intel`（不是 dolans-brief）**
**GitHub Pages 源：bibi-intel 的 `/docs` 目录**

输出文件必须放在 `docs/daily_brief_YYYY-MM-DD.html`，GitHub Pages 才能正确服务。

完成 HTML 后：
1. 写入 `data/daily_brief_YYYY-MM-DD.html`
2. 复制到 `docs/daily_brief_YYYY-MM-DD.html`
3. `git add docs/daily_brief_YYYY-MM-DD.html`
4. `git commit -m "publish: Dolan's Brief YYYY-MM-DD"`
5. `git push origin main`

## 设计规范（强制约束）

**严禁深色 Terminal/Bloomberg 风格。必须使用以下精确规范：**

| 属性 | 值 |
|------|-----|
| 背景色 | `#faf9f6`（米白，非深色） |
| 卡片背景 | `#ffffff` |
| 正文色 | `#222222` |
| 标题字 | Noto Serif SC, Georgia, serif |
| 正文字 | Noto Sans SC, sans-serif |
| 卡片最大宽度 | 800px |
| 响应式断点 | 640px |

**不允许**：
- 深色背景（#0a0e14 等）
- 霓虹绿/霓虹蓝等高亮色
- Bloomberg Terminal 风格
- 任何自创设计风格

**推荐字体（必须通过 Google Fonts link 加载）**：
```html
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;700&family=Noto+Serif+SC:wght@400;600;700&display=swap" rel="stylesheet">
```

## GitHub Pages URL 格式

完成推送后，GitHub Pages 访问地址为：
```
https://dolan9644.github.io/bibi-intel/daily_brief_YYYY-MM-DD.html
```

**不是** `dolans-brief`，不是 jsDelivr，不是其他 CDN。

## 沟通规则

完成工作后通过 sessions_spawn 的 announce 机制回报结果给 bibi-agent。
不需要主动联系用户。
