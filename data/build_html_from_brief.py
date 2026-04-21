#!/usr/bin/env python3
"""
Dolan's 全景内参 HTML 渲染器
稳健版，直接消费当前 brief_content.txt 的自然文本结构。
"""

import html
import os
import re
import sys
from datetime import datetime

DATE = sys.argv[1] if len(sys.argv) > 1 else datetime.now().strftime("%Y-%m-%d")
WEEKDAY = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']

try:
    d = datetime.strptime(DATE, "%Y-%m-%d")
    DATE_DISPLAY = f"{d.year} 年 {d.month} 月 {d.day} 日 · {WEEKDAY[d.weekday()]}"
except Exception:
    DATE_DISPLAY = DATE

BASE = "/Users/dolan/.openclaw/agents/bibi-agent"
BRIEF_FILE = f"{BASE}/data/brief_content.txt"
OUTPUT_FILE = f"{BASE}/docs/daily_brief_{DATE}.html"
BACKUP_FILE = f"/tmp/daily_brief_{DATE}.html"

with open(BRIEF_FILE, "r", encoding="utf-8") as f:
    raw = f.read()


def section_slice(text, start_patterns, end_patterns=None):
    start_patterns = start_patterns if isinstance(start_patterns, (list, tuple)) else [start_patterns]
    end_patterns = end_patterns if isinstance(end_patterns, (list, tuple)) else ([end_patterns] if end_patterns else [])
    start = None
    for pat in start_patterns:
        m = re.search(pat, text, flags=re.MULTILINE)
        if m and (start is None or m.start() < start):
            start = m.start()
    if start is None:
        return ""
    tail = text[start:]
    end = len(tail)
    for pat in end_patterns:
        m = re.search(pat, tail, flags=re.MULTILINE)
        if m and m.start() < end:
            end = m.start()
    return tail[:end].strip()


def linkify(text):
    escaped = html.escape(text)
    return re.sub(r'(https?://[^\s<]+)', r'<a href="\1" target="_blank">\1</a>', escaped)


def paragraphize(text):
    blocks = [b.strip() for b in re.split(r'\n\s*\n', text.strip()) if b.strip()]
    out = []
    for b in blocks:
        out.append(f"<p>{linkify(b).replace(chr(10), '<br>')}</p>")
    return "\n".join(out)


def split_core(text):
    text = re.sub(r'^(【核心阵地】|核心阵地)\s*\n+', '', text, flags=re.MULTILINE).strip()
    blocks = [b.strip() for b in re.split(r'(?=^[一二三四五六七八九十]+、)', text, flags=re.MULTILINE) if b.strip()]
    items = []
    for block in blocks:
        lines = block.splitlines()
        title = lines[0].strip()
        body = '\n'.join(lines[1:]).strip()
        items.append((title, body))
    return items


def split_giants(text):
    text = re.sub(r'^(【巨头绞肉机】|巨头绞肉机)\s*\n+', '', text, flags=re.MULTILINE).strip()
    summary = ""
    items_text = text
    summary_m = re.search(r"\nDolan['’]s 锐评：(?!(这不是模型更会画|中国开源模型现在不是追赶剧|Anthropic 终于不装清高|这不是功能调整|一堆团队嘴上喊 AI Native|当用户开始自己搭日程系统|AI 把补丁生成成本打到地板|代码越来越便宜|本地 AI 让电脑重新变成生产资料|一堆现实世界系统还活在|今天大家都在拼大脑|自动写码的上限)).+?$", text, flags=re.DOTALL)
    if summary_m:
        summary = summary_m.group(0).strip()
        items_text = text[:summary_m.start()].rstrip()
    blocks = [b.strip() for b in re.split(r'(?=^\d+\.\s+核心事件：)', items_text, flags=re.MULTILINE) if b.strip()]
    items = []
    for block in blocks:
        lines = [ln.strip() for ln in block.splitlines() if ln.strip()]
        if not lines:
            continue
        title = re.sub(r'^\d+\.\s+核心事件：', '', lines[0]).strip()
        body = '\n'.join(lines[1:]).strip()
        items.append((title, body))
    if not summary:
        last_review = re.search(r"(Dolan['’]s 锐评：今天大厂和平台.*)$", text, flags=re.DOTALL)
        if last_review:
            summary = last_review.group(1).strip()
    return items, summary


def split_radar(text):
    text = re.sub(r'^(【极客雷达】|极客雷达)\s*\n+', '', text, flags=re.MULTILINE).strip()
    summary = ""
    summary_m = re.search(r"\nDolan['’]s 锐评：极客圈今天最有意思的暗流.*$", text, flags=re.DOTALL)
    if summary_m:
        summary = summary_m.group(0).strip()
        items_text = text[:summary_m.start()].rstrip()
    else:
        items_text = text
    blocks = [b.strip() for b in re.split(r'(?=^\d+\.\s+)', items_text, flags=re.MULTILINE) if b.strip()]
    items = []
    for block in blocks:
        lines = [ln.strip() for ln in block.splitlines() if ln.strip()]
        if not lines:
            continue
        title = re.sub(r'^\d+\.\s+', '', lines[0]).strip()
        body = '\n'.join(lines[1:]).strip()
        items.append((title, body))
    return items, summary


subtitle_m = re.search(r"^Title:\s*Dolan['’]s 全景内参[：:]\s*(.+)$", raw, flags=re.MULTILINE)
subtitle = subtitle_m.group(1).strip() if subtitle_m else DATE_DISPLAY
core_raw = section_slice(raw, [r'^核心阵地\s*$', r'^【核心阵地】\s*$'], [r'^巨头绞肉机\s*$', r'^【巨头绞肉机】\s*$'])
giants_raw = section_slice(raw, [r'^巨头绞肉机\s*$', r'^【巨头绞肉机】\s*$'], [r'^极客雷达\s*$', r'^【极客雷达】\s*$'])
radar_raw = section_slice(raw, [r'^极客雷达\s*$', r'^【极客雷达】\s*$'], [r'^终局研判\s*$'])
final_raw = section_slice(raw, [r'^终局研判\s*$'], [r'\Z'])
final_raw = re.sub(r'^终局研判\s*\n+', '', final_raw, flags=re.MULTILINE)

core_items = split_core(core_raw)
giants_items, giants_summary = split_giants(giants_raw)
radar_items, radar_summary = split_radar(radar_raw)
final_text = re.sub(r"^Dolan['’]s 致命锐评：\s*", '', final_raw.strip())

parts = [f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Dolan's 全景内参 | {html.escape(subtitle)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;500;600;700&family=Noto+Sans+SC:wght@400;500;700;900&display=swap" rel="stylesheet">
<style>
* {{ box-sizing: border-box; }}
body {{ margin: 0; background: #faf9f6; color: #222; font-family: 'Noto Serif SC', serif; line-height: 1.82; }}
a {{ color: #7a1d1d; text-decoration: none; }}
a:hover {{ text-decoration: underline; }}
.container {{ max-width: 800px; margin: 0 auto; padding: 56px 28px 84px; }}
.masthead {{ padding-bottom: 34px; border-bottom: 2px solid #222; margin-bottom: 42px; }}
.kicker {{ font: 700 12px/1.4 'Noto Sans SC', sans-serif; letter-spacing: 0.18em; text-transform: uppercase; color: #8a8a8a; margin-bottom: 16px; }}
.title {{ font: 900 34px/1.25 'Noto Sans SC', sans-serif; color: #111; margin: 0 0 12px; }}
.subtitle {{ font-size: 18px; color: #4e4e4e; }}
.section-header {{ margin: 56px 0 28px; font: 800 13px/1.4 'Noto Sans SC', sans-serif; letter-spacing: 0.2em; text-transform: uppercase; color: #666; display: flex; align-items: center; gap: 12px; }}
.section-header::after {{ content: ''; height: 1px; flex: 1; background: #ddd; }}
.article {{ margin-bottom: 42px; }}
.article-title {{ font: 800 24px/1.4 'Noto Sans SC', sans-serif; color: #111; margin-bottom: 14px; }}
.article-body p, .giant-body p, .radar-body p, .summary p, .final-body p {{ margin: 0 0 14px; font-size: 17px; }}
.quote-block {{ background: #fff8dc; border-left: 4px solid #b30000; padding: 16px 18px; margin-top: 16px; }}
.quote-label {{ font: 800 12px/1.4 'Noto Sans SC', sans-serif; letter-spacing: 0.12em; text-transform: uppercase; color: #b30000; margin-bottom: 8px; }}
.divider {{ border: none; border-top: 1px solid #e7e2da; margin: 42px 0; }}
.giant-item {{ margin-bottom: 28px; }}
.giant-title {{ font: 800 20px/1.45 'Noto Sans SC', sans-serif; margin-bottom: 10px; color: #111; }}
.radar-item {{ display: grid; grid-template-columns: 44px 1fr; gap: 12px; padding: 18px 0; border-bottom: 1px solid #eee; }}
.radar-num {{ font: 800 12px/1.6 'Noto Sans SC', sans-serif; color: #bbb; padding-top: 3px; }}
.radar-title {{ font: 700 18px/1.45 'Noto Sans SC', sans-serif; color: #111; margin-bottom: 6px; }}
.final-section {{ margin-top: 16px; background: #171717; padding: 30px 28px; color: #ededed; }}
.final-title {{ font: 800 13px/1.4 'Noto Sans SC', sans-serif; letter-spacing: 0.16em; text-transform: uppercase; color: #ff7a7a; margin-bottom: 14px; }}
.outro {{ margin-top: 58px; padding-top: 24px; border-top: 1px solid #ece7df; text-align: center; font: 500 12px/1.8 'Noto Sans SC', sans-serif; color: #999; }}
@media (max-width: 640px) {{ .container {{ padding: 36px 18px 72px; }} .title {{ font-size: 28px; }} .article-title {{ font-size: 22px; }} .giant-title {{ font-size: 18px; }} }}
</style>
</head>
<body>
<div class="container">
<header class="masthead">
<div class="kicker">{DATE_DISPLAY}</div>
<h1 class="title">Dolan's 全景内参</h1>
<div class="subtitle">{html.escape(subtitle)}</div>
</header>
''']

parts.append('<section>\n<div class="section-header">🎯 核心阵地</div>\n')
for title, body in core_items:
    parts.append(f'<article class="article"><div class="article-title">{html.escape(title)}</div><div class="article-body">{paragraphize(body)}</div></article>\n')
parts.append('</section>\n<hr class="divider">\n')

parts.append('<section>\n<div class="section-header">🌍 巨头绞肉机</div>\n')
for title, body in giants_items:
    parts.append(f'<div class="giant-item"><div class="giant-title">{html.escape(title)}</div><div class="giant-body">{paragraphize(body)}</div></div>\n')
if giants_summary:
    parts.append(f'<div class="quote-block summary"><div class="quote-label">板块总结</div><p>{linkify(giants_summary).replace(chr(10), "<br>")}</p></div>\n')
parts.append('</section>\n<hr class="divider">\n')

parts.append('<section>\n<div class="section-header">📡 极客雷达</div>\n')
for idx, (title, body) in enumerate(radar_items, 1):
    parts.append(f'<div class="radar-item"><div class="radar-num">{idx:02d}</div><div><div class="radar-title">{html.escape(title)}</div><div class="radar-body">{paragraphize(body)}</div></div></div>\n')
if radar_summary:
    parts.append(f'<div class="quote-block summary"><div class="quote-label">板块总结</div><p>{linkify(radar_summary).replace(chr(10), "<br>")}</p></div>\n')
parts.append('</section>\n<hr class="divider">\n')

parts.append('<section>\n<div class="section-header">💡 终局研判</div>\n')
parts.append(f'<div class="final-section"><div class="final-title">Dolan\'s 致命锐评</div><div class="final-body">{paragraphize(final_text)}</div></div>\n')
parts.append('</section>\n')
parts.append(f'<div class="outro">Dolan\'s 全景内参 · {DATE} · 仅供个人研究参考<br>锐评由 LLM 生成，链接与事实以原始来源为准</div>\n')
parts.append('</div>\n</body>\n</html>\n')

result = ''.join(parts)
os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    f.write(result)
with open(BACKUP_FILE, 'w', encoding='utf-8') as f:
    f.write(result)

print(f'✅ HTML生成完成：{OUTPUT_FILE} ({os.path.getsize(OUTPUT_FILE)} bytes)')
print(f'✅ 备份：{BACKUP_FILE}')
print(f'✅ 统计：核心阵地 {len(core_items)} 篇 | 巨头 {len(giants_items)} 条 | 雷达 {len(radar_items)} 条')
