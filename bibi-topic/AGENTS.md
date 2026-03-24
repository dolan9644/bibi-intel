# AGENTS.md — BIBI Topic

## 启动仪式

1. 读 SOUL.md — 理解你的情报官身份
2. 读 IDENTITY.md — 确认你的角色标识
3. 检查 `/Users/dolan/.openclaw/agents/bibi-agent/data/` 下近 7 天的 topic_result_*.json 用于查重

## 核心职责

收到 bibi-agent 的 spawn 指令后：
1. 读取 `data/raw_rss.json`（RSS 清洗后的原始内容）
2. 执行 6 维情报雷达扫描
3. 对比前 7 天历史数据，语义去重
4. 按 Tier 分级写入 `data/topic_result.json`

## 文件协议

- 读：`/Users/dolan/.openclaw/agents/bibi-agent/data/raw_rss.json`
- 写：`/Users/dolan/.openclaw/agents/bibi-agent/data/topic_result.json`
- 查重：`/Users/dolan/.openclaw/agents/bibi-agent/data/topic_result_YYYY-MM-DD.json`（近7天）

## 沟通规则

完成工作后通过 sessions_spawn 的 announce 机制回报结果给 bibi-agent。
不需要主动联系用户。
