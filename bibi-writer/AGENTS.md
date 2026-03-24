# AGENTS.md — BIBI Writer

## 启动仪式

1. 读 SOUL.md — 理解你的主笔身份和叙事结构
2. 读 IDENTITY.md — 确认你的角色标识
3. 读取 `/Users/dolan/.openclaw/agents/bibi-agent/data/topic_result.json`

## 核心职责

收到 bibi-agent 的 spawn 指令后：
1. 读取 `data/topic_result.json`（bibi-topic 去重后的 JSON 情报）
2. 撰写四板块内参：核心阵地 / 巨头绞肉机 / 极客雷达 / 终局研判
3. 大佬内容必须附上来源链接
4. 输出到 `data/brief_content.txt`（纯文本，代码片段不以 Markdown 代码块呈现）

## 文件协议

- 读：`/Users/dolan/.openclaw/agents/bibi-agent/data/topic_result.json`
- 写：`/Users/dolan/.openclaw/agents/bibi-agent/data/brief_content.txt`

## 沟通规则

完成工作后通过 sessions_spawn 的 announce 机制回报结果给 bibi-agent。
不需要主动联系用户。
