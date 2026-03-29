# Dolan's AI Morning Brief 工作流手册
> 维护人：Dolan | 更新日期：2026-03-29

## 流程概览

Cron Job ID：`0eef9649-42e1-4bc3-822f-dc155181e934`
Schedule：`0 6 * * *`（每天早上 6:00 北京时间）
触发命令：`openclaw cron run 0eef9649-42e1-4bc3-822f-dc155181e934`

### 完整流程（8步）

```
Step 1 → 抓取RSS原始数据（fetch_all_rss.py）
Step 2 → 生成选题结构（build_topic_retry.py）
Step 3 → bibi-topic 情报分析（T0-T4分级）
Step 4 → bibi-writer 撰写全文
Step 5 → bibi-design HTML渲染
Step 6 → GitHub Pages 确认+触发重建
Step 7 → 飞书推送卡片
Step 8 → 数据备份验证
```

## 各 Agent 配置路径

| Agent | SOUL.md | AGENTS.md | 输入 | 输出 |
|-------|---------|-----------|------|------|
| bibi-topic | `bibi-topic/SOUL.md` | `bibi-topic/AGENTS.md` | `data/topic_result.json` | `data/topic_result.json`（覆盖）|
| bibi-writer | `bibi-writer/SOUL.md` | `bibi-writer/AGENTS.md` | `data/topic_result.json` | `data/brief_content.txt` |
| bibi-design | `bibi-design/SOUL.md` | `bibi-design/AGENTS.md` | `data/brief_content.txt` | `data/daily_brief_YYYY-MM-DD.html` + `docs/daily_brief_YYYY-MM-DD.html` |

## HTML 渲染引擎

渲染脚本：`data/build_html_from_brief.py`（v5，稳定版）

**2026-03-29 修复记录**：writer 输出格式改为中文括号 `【核心阵地】【巨头绞肉机】【极客雷达】`，parser 同步对齐。

Section 分割正则：`re.split(r'(?=【(?:核心阵地|巨头绞肉机|极客雷达)】)', raw)`

如再次出现空内容问题，优先检查：
1. Section 分割正则是否匹配当前 writer 输出格式
2. 代码块标记：`代码/配置演示——` 还是 `代码/配置演示（生产环境可用）`
3. pycache 是否过期（删除 `__pycache__/*.pyc`）

## 极客雷达格式规范（2026-03-26 修订）

**标准格式（管道符分隔）：**
```
名称：产品全称+一句话说明 | GitHub热度：X | 痛点解决：Y | 为什么值得关注：Z
```

**名称字段要求**：
- 必须让读者一眼看懂是什么+做什么用
- 15-30 字，不能是单个词汇
- 示例：`VTAM（视觉-触觉统一模型）` 而不是 `VTAM`

## GitHub Pages

- Repo：`dolan9644/bibi-intel`
- 分支：`main`
- 发布目录：`docs/`
- URL：`https://dolan9644.github.io/bibi-intel/daily_brief_YYYY-MM-DD.html`
- 触发重建：`POST https://api.github.com/repos/dolan9644/bibi-intel/pages/builds`

## 质量门槛

| 指标 | 最低要求 | 理想值 |
|------|---------|--------|
| HTML 大小 | > 15KB | > 30KB |
| 核心阵地 | ≥ 2篇 | 2篇，每篇 800+字 |
| 巨头绞肉机 | ≥ 10条 | 10条 |
| 极客雷达 | ≤ 30条 | 10-15条 |
| brief_content.txt | > 12KB | > 25KB |

## 常见问题

### Q: HTML 内容为空（6KB）但设计检查全过
A: `build_html_from_brief.py` 正则匹配失效。执行：
```bash
rm -f data/__pycache__/*.pyc
python3 data/build_html_from_brief.py YYYY-MM-DD
```

### Q: 雷达名称只显示单词
A: writer 的 `bibi-writer/SOUL.md` 中已规定名称字段格式。检查 writer 是否遵循了"产品全称+一句话说明"的要求。

### Q: 极客雷达 SUMMARY 显示空
A: 检查 `## Dolan's 锐评：板块总结` 是否在 radar 板块内，且格式正确。
