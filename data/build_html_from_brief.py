#!/usr/bin/env python3
"""
Dolan's 全景内参 - HTML渲染引擎 v5 (Stable)
从 brief_content.txt 生成符合 SOUL.md 设计规范的 HTML
兼容 writer 中文括号格式【核心阵地】【巨头绞肉机】【极客雷达】
"""
import re, sys, os
from datetime import datetime

DATE = sys.argv[1] if len(sys.argv) > 1 else datetime.now().strftime("%Y-%m-%d")
WEEKDAY = ['周一','周二','周三','周四','周五','周六','周日']
try:
    d = datetime.strptime(DATE, "%Y-%m-%d")
    wd = WEEKDAY[d.weekday()]
    DATE_DISPLAY = f"{d.year} 年 {d.month} 月 {d.day} 日 · {wd}"
except:
    DATE_DISPLAY = DATE

BASE = "/Users/dolan/.openclaw/agents/bibi-agent"
BRIEF_FILE = f"{BASE}/data/brief_content.txt"
OUTPUT_FILE = f"{BASE}/data/daily_brief_{DATE}.html"
BACKUP_FILE = f"/tmp/daily_brief_{DATE}.html"

# ============================================================
# 读取源文件
# ============================================================
with open(BRIEF_FILE) as f:
    raw = f.read()

# ============================================================
# 解析标题
# ============================================================
title_match = re.search(r"Title:\s*Dolan[']s 全景内参[：:]\s*(.+?)\n", raw)
subtitle = title_match.group(1).strip() if title_match else DATE_DISPLAY

# ============================================================
# Section 分割：按【】中文括号分割各板块（writer 输出格式）
# ============================================================
# parts[0] = Title 行 + 核心阵地之前的内容
# parts[1] = 【核心阵地】 + 内容
# parts[2] = 【巨头绞肉机】 + 内容
# parts[3] = 【极客雷达】 + 内容（包含 终局研判，以 ## Dolan's 致命锐评 分割）
parts = re.split(r'(?=【(?:核心阵地|巨头绞肉机|极客雷达)】)', raw)

def safe_get(arr, idx, default=''):
    return arr[idx] if idx < len(arr) else default

core_raw = safe_get(parts, 1, '')
giants_raw = safe_get(parts, 2, '')
# 极客雷达和终局研判在 parts[3] 里，用 ## Dolan's 致命锐评： 分割
radar_combined = safe_get(parts, 3, '')

# 从 radar_combined 中分离极客雷达和终局研判
if "## Dolan's 致命锐评" in radar_combined:
    radar_raw, final_raw = radar_combined.split("## Dolan's 致命锐评", 1)
else:
    radar_raw = radar_combined
    final_raw = ''
final_raw = safe_get(parts, 4, '')

# ============================================================
# 辅助函数
# ============================================================
def clean_md(text):
    """Markdown -> HTML"""
    if not text:
        return ''
    text = re.sub(r'```[\w]*\n(.*?)```', r'<pre><code>\1</code></pre>', text, flags=re.DOTALL)
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', text)
    return text

def to_paragraphs(text):
    """将文本分段包装为 <p>"""
    if not text:
        return ''
    blocks = re.split(r'\n\n+', text)
    out = []
    for b in blocks:
        b = b.strip()
        if not b:
            continue
        if '<pre>' in b:
            out.append(clean_md(b))
        else:
            out.append(f'<p>{clean_md(b)}</p>')
    return '\n'.join(out)

# ============================================================
# 解析核心阵地
# Writer格式:
#   【核心阵地】
#   【深度文章一】Title
#   背景溯源：...
#   完整分析：...
#   代码/配置演示——标题：
#   ...code...
#   Dolan's 锐评：...
#   【深度文章二】Title
#   ...
# ============================================================
def parse_core_articles(core_text):
    articles = []
    # 去掉板块头部【核心阵地】
    text = re.sub(r'^【核心阵地】\n+', '', core_text)
    text = re.sub(r'^### \U0001F3AF[^\n]*\n+', '', text)
    
    # 按【文章分割
    blocks = re.split(r'(?=\n【(?:深度)?文章[一二三四五六七八九十]+】)', text)
    
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        
        # 提取标题: 【深度文章一】Title
        title_m = re.match(r'【(?:深度)?文章[一二三四五六七八九十]+】(.+?)(：|$)', block)
        if title_m:
            title = title_m.group(1).strip()
        else:
            first_line = block.split('\n')[0]
            title = re.sub(r'^【.+?】', '', first_line).strip()
        
        # 提取各部分
        bj_m = re.search(r'背景溯源[：:]\s*(.+?)(?=\n完整分析|\n代码|\nDolan[\'\\u0027]s)', block, re.DOTALL)
        beijing = bj_m.group(1).strip() if bj_m else ''
        
        fx_m = re.search(r'完整分析[：:]\s*(.+?)(?=\n代码|\nDolan[\'\\u0027]s)', block, re.DOTALL)
        fenxi = fx_m.group(1).strip() if fx_m else ''
        
        code_m = re.search(r'代码/配置演示[（——][^）\n]*[)）:：]\s*(?:```?\w*\n)?(.+?)(?=\nDolan[\'\\u0027]s|\Z)', block, re.DOTALL)
        code_text = code_m.group(1).strip() if code_m else ''
        
        rj_m = re.search(r"Dolan['\u0027]s 锐评[：:]\s*(.+?)(?=\n【|\Z)", block, re.DOTALL)
        review = rj_m.group(1).strip() if rj_m else ''
        
        links = re.findall(r'(https?://\S+)', block)
        
        articles.append({
            'title': clean_md(title),
            'beijing': clean_md(beijing),
            'fenxi': clean_md(fenxi),
            'code': code_text,
            'review': clean_md(review),
            'links': links,
        })
    
    return articles

# ============================================================
# 解析巨头绞肉机
# Writer格式:
#   [核心事件]：描述
#   [关键细节]：描述
#   Dolan's 锐评：描述
#   [核心事件]：描述 (next)
#   ...
#   ## Dolan's 锐评：板块总结——...
# ============================================================
def parse_giants(giants_text):
    items = []
    text = re.sub(r'^【巨头绞肉机】\n+', '', giants_text)
    
    # 提取板块总结
    summary_m = re.search(r"## Dolan['\u0027]s 锐评[：:]板块总结[——:]*(.+?)$", text, re.DOTALL)
    summary = summary_m.group(1).strip() if summary_m else ''
    text_no_summary = re.sub(r"\n## Dolan['\u0027]s 锐评[：:]板块总结[——:]*.*$", '', text, flags=re.DOTALL)
    
    # 按 [核心事件]：分割
    blocks = re.split(r'(?=\n\[核心事件\])', text_no_summary)
    
    for block in blocks:
        block = block.strip()
        if not block or block.startswith('🌍'):
            continue
        
        event_m = re.match(r'\[核心事件\][：:]\s*(.+?)(?=\n\[关键细节\]|\nDolan|$)', block, re.DOTALL)
        event = event_m.group(1).strip() if event_m else ''
        
        detail_m = re.search(r'\[关键细节\][：:]\s*(.+?)(?=\nDolan)', block, re.DOTALL)
        details = detail_m.group(1).strip() if detail_m else ''
        
        review_m = re.search(r"Dolan['\u0027]s 锐评[：:]\s*(.+?)$", block, re.DOTALL)
        review = review_m.group(1).strip() if review_m else ''
        
        if event:
            items.append({
                'event': clean_md(event),
                'details': clean_md(details),
                'review': clean_md(review),
            })
    
    return items, clean_md(summary)

# ============================================================
# 解析极客雷达
# Writer格式:
#   名称：X | GitHub热度：Y | 痛点解决：Z | 为什么值得关注：W
#   ...
#   ## Dolan's 锐评：板块总结——...
# ============================================================
def parse_radar(radar_text):
    items = []
    # 极客雷达和终局研判在同一个 raw 块里，用 ## Dolan's 致命锐评： 分割
    radar_only = re.split(r'(?=## Dolan[\'"]s 致命锐评)', radar_text)[0]
    text = re.sub(r'^【极客雷达】\n+', '', radar_only)
    
    # 提取板块总结
    summary_m = re.search(r"## Dolan['\u0027]s 锐评[：:]板块总结[——:]*(.+?)$", text, re.DOTALL)
    summary = summary_m.group(1).strip() if summary_m else ''
    text_no_summary = re.sub(r"\n## Dolan['\u0027]s 锐评[：:]板块总结[——:]*.*$", '', text, flags=re.DOTALL)
    
    for line in text_no_summary.split('\n'):
        line = line.strip()
        if not line or line.startswith('📡'):
            continue
        
        name_m = re.search(r'名称[：:](.+?)(?:\||GitHub)', line)
        hot_m = re.search(r'GitHub热度[：:](.+?)(?:\||痛点)', line)
        pain_m = re.search(r'痛点解决[：:](.+?)(?:\||为什么)', line)
        why_m = re.search(r'为什么值得关注[：:](.+?)$', line)
        
        name = name_m.group(1).strip() if name_m else ''
        if name:
            items.append({
                'name': clean_md(name),
                'hot': clean_md(hot_m.group(1).strip() if hot_m else ''),
                'pain': clean_md(pain_m.group(1).strip() if pain_m else ''),
                'why': clean_md(why_m.group(1).strip() if why_m else ''),
            })
    
    return items, clean_md(summary)

# ============================================================
# 解析终局研判
# ============================================================
def parse_final(final_text):
    text = re.sub(r'^💡[^\n]*\n+', '', final_text)
    text = re.sub(r"^## Dolan['\u0027]s 致命锐评[：:]\n*", '', text, flags=re.MULTILINE)
    return clean_md(text.strip())

# ============================================================
# 执行解析
# ============================================================
core_articles = parse_core_articles(core_raw)
giants_items, giants_summary = parse_giants(giants_raw)
radar_items, radar_summary = parse_radar(radar_raw)
final_text = parse_final(final_raw)

# ============================================================
# HTML 构建
# ============================================================
html_parts = []

# Head/Base CSS
html_parts.append(f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Dolan&apos;s 全景内参：{clean_md(subtitle)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;500;600;700&family=Noto+Sans+SC:wght@300;400;500;700&display=swap" rel="stylesheet">
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
html {{ font-size: 17px; }}
body {{ background-color: #faf9f6; color: #222; font-family: 'Noto Serif SC', serif; line-height: 1.75; -webkit-font-smoothing: antialiased; }}
.container {{ max-width: 800px; margin: 0 auto; padding: 60px 32px 100px; }}
.masthead {{ padding-bottom: 48px; border-bottom: 2px solid #222; margin-bottom: 56px; }}
.masthead-date {{ font-family: 'Noto Sans SC', sans-serif; font-size: 0.75rem; font-weight: 500; letter-spacing: 0.15em; color: #888; text-transform: uppercase; margin-bottom: 16px; }}
.masthead-title {{ font-family: 'Noto Sans SC', sans-serif; font-size: 1.6rem; font-weight: 700; color: #111; line-height: 1.3; margin-bottom: 12px; letter-spacing: -0.01em; }}
.masthead-subtitle {{ font-size: 1rem; color: #555; font-weight: 400; line-height: 1.6; }}
.section-header {{ font-family: 'Noto Sans SC', sans-serif; font-size: 0.78rem; font-weight: 700; letter-spacing: 0.2em; color: #666; text-transform: uppercase; margin-bottom: 36px; margin-top: 64px; display: flex; align-items: center; gap: 10px; }}
.section-header::after {{ content: ''; flex: 1; height: 1px; background: #ddd; }}
.article {{ margin-bottom: 52px; }}
.article-title {{ font-family: 'Noto Sans SC', sans-serif; font-size: 1.05rem; font-weight: 600; color: #111; line-height: 1.45; margin-bottom: 14px; letter-spacing: -0.005em; }}
.article-meta {{ font-family: 'Noto Sans SC', sans-serif; font-size: 0.8rem; color: #888; margin-bottom: 16px; }}
.article-meta a {{ color: #999; text-decoration: none; }}
.article-meta a:hover {{ color: #555; }}
.article-body {{ font-size: 0.95rem; color: #333; line-height: 1.8; }}
.article-body p {{ margin-bottom: 14px; }}
.article-body pre {{ background: #f3f3f3; border-left: 3px solid #ccc; padding: 12px 16px; overflow-x: auto; margin: 16px 0; font-size: 0.85rem; line-height: 1.5; }}
.article-body code {{ background: #f3f3f3; padding: 2px 6px; font-size: 0.85em; border-radius: 3px; }}
.quote-block {{ background: #fff8dc; border-left: 4px solid #b30000; padding: 16px 20px; margin: 20px 0; }}
.quote-label {{ font-family: 'Noto Sans SC', sans-serif; font-size: 0.75rem; font-weight: 700; letter-spacing: 0.1em; color: #b30000; text-transform: uppercase; margin-bottom: 8px; }}
.quote-block p {{ color: #333; font-size: 0.9rem; line-height: 1.7; margin: 0; }}
.section-summary {{ margin-top: 24px; }}
.giant-item {{ margin-bottom: 36px; }}
.giant-title {{ font-family: 'Noto Sans SC', sans-serif; font-size: 1rem; font-weight: 600; color: #111; margin-bottom: 10px; line-height: 1.4; }}
.giant-body {{ font-size: 0.9rem; color: #333; line-height: 1.75; }}
.giant-body p {{ margin-bottom: 10px; }}
.radar-item {{ display: flex; gap: 16px; margin-bottom: 20px; padding-bottom: 20px; border-bottom: 1px solid #eee; }}
.radar-item:last-child {{ border-bottom: none; }}
.radar-num {{ font-family: 'Noto Sans SC', sans-serif; font-size: 0.7rem; font-weight: 700; color: #bbb; min-width: 24px; padding-top: 2px; }}
.radar-content {{ flex: 1; }}
.radar-title {{ font-family: 'Noto Sans SC', sans-serif; font-size: 0.9rem; font-weight: 600; color: #111; margin-bottom: 4px; }}
.radar-desc {{ font-size: 0.85rem; color: #555; line-height: 1.6; }}
.radar-link {{ font-size: 0.78rem; color: #999; margin-top: 4px; }}
.radar-link a {{ color: #aaa; text-decoration: none; }}
.radar-link a:hover {{ color: #666; }}
.final-section {{ background: #1a1a1a; color: #f0f0f0; padding: 36px 32px; margin-top: 48px; }}
.final-header {{ font-family: 'Noto Sans SC', sans-serif; font-size: 0.78rem; font-weight: 700; letter-spacing: 0.15em; color: #ff6b6b; text-transform: uppercase; margin-bottom: 16px; }}
.final-body {{ font-size: 0.95rem; line-height: 1.8; color: #ddd; }}
.divider {{ border: none; border-top: 1px solid #eee; margin: 48px 0; }}
.outro {{ text-align: center; font-family: 'Noto Sans SC', sans-serif; font-size: 0.75rem; color: #bbb; margin-top: 64px; padding-top: 24px; border-top: 1px solid #eee; }}
@media (max-width: 640px) {{ .container {{ padding: 40px 20px 80px; }} .masthead-title {{ font-size: 1.3rem; }} }}
</style>
</head>
<body>
<div class="container">
<header class="masthead">
<div class="masthead-date">{DATE_DISPLAY}</div>
<div class="masthead-title">Dolan&apos;s 全景内参</div>
<div class="masthead-subtitle">{clean_md(subtitle)}</div>
</header>
''')

# 核心阵地
html_parts.append('<div class="section-header">🎯 核心阵地：智能体与协作框架深潜</div>\n')
for art in core_articles:
    html_parts.append('<div class="article">\n')
    html_parts.append(f'<div class="article-title">■ {art["title"]}</div>\n')
    if art['links']:
        links_html = ' · '.join(f'<a href="{l}" target="_blank">{l[:40]}...</a>' for l in art['links'])
        html_parts.append(f'<div class="article-meta">{links_html}</div>\n')
    html_parts.append('<div class="article-body">\n')
    if art['beijing']:
        html_parts.append(f'<p>{art["beijing"]}</p>\n')
    if art['fenxi']:
        html_parts.append(f'<p>{art["fenxi"]}</p>\n')
    if art['code']:
        html_parts.append(f'<pre><code>{art["code"]}</code></pre>\n')
    if art['review']:
        html_parts.append(f'''<div class="quote-block">
<div class="quote-label">Dolan&apos;s 锐评</div>
<p>{art["review"]}</p>
</div>\n''')
    html_parts.append('</div>\n</div>\n')

html_parts.append('<hr class="divider">\n')

# 巨头绞肉机
html_parts.append('<div class="section-header">🌍 巨头绞肉机：大模型底座与算力</div>\n')
for item in giants_items:
    html_parts.append('<div class="giant-item">\n')
    html_parts.append(f'<div class="giant-title">■ {item["event"]}</div>\n')
    html_parts.append('<div class="giant-body">\n')
    if item['details']:
        html_parts.append(f'<p>{item["details"]}</p>\n')
    if item['review']:
        html_parts.append(f'''<div class="quote-block">
<div class="quote-label">Dolan&apos;s 锐评</div>
<p>{item["review"]}</p>
</div>\n''')
    html_parts.append('</div>\n</div>\n')
if giants_summary:
    html_parts.append(f'''<div class="quote-block section-summary">
<div class="quote-label">Dolan&apos;s 锐评：板块总结</div>
<p>{giants_summary}</p>
</div>\n''')

html_parts.append('<hr class="divider">\n')

# 极客雷达
html_parts.append('<div class="section-header">📡 极客雷达：高潜开源与暗流</div>\n')
for i, item in enumerate(radar_items, 1):
    html_parts.append('<div class="radar-item">\n')
    html_parts.append(f'<div class="radar-num">{i}</div>\n')
    html_parts.append('<div class="radar-content">\n')
    html_parts.append(f'<div class="radar-title">{item["name"]}</div>\n')
    if item['pain']:
        html_parts.append(f'<div class="radar-desc"><strong>痛点：</strong>{item["pain"]}</div>\n')
    if item['why']:
        html_parts.append(f'<div class="radar-desc"><em>为何值得关注：{item["why"]}</em></div>\n')
    html_parts.append('</div>\n</div>\n')
if radar_summary:
    html_parts.append(f'''<div class="quote-block section-summary">
<div class="quote-label">Dolan&apos;s 锐评：板块总结</div>
<p>{radar_summary}</p>
</div>\n''')

html_parts.append('<hr class="divider">\n')

# 终局研判
html_parts.append('<div class="section-header">💡 终局研判</div>\n')
if final_text:
    html_parts.append(f'''<div class="final-section">
<div class="final-header">Dolan&apos;s 致命锐评</div>
<div class="final-body">
<p>{final_text}</p>
</div>
</div>\n''')

# Outro
html_parts.append(f'''
<div class="outro">
Dolan&apos;s 全景内参 · {DATE} · 仅供个人研究参考<br>
锐评由LLM生成 | 内容仅供参考
</div>
</div><!-- container -->
</body>
</html>
''')

# ============================================================
# 写入文件
# ============================================================
html = ''.join(html_parts)
with open(OUTPUT_FILE, "w") as f:
    f.write(html)

size = os.path.getsize(OUTPUT_FILE)
print(f"✅ HTML生成完成：{OUTPUT_FILE} ({size} bytes)")

with open(OUTPUT_FILE) as src, open(BACKUP_FILE, "w") as dst:
    dst.write(src.read())
print(f"✅ 备份：{BACKUP_FILE}")

# ============================================================
# 设计规范自检
# ============================================================
checks = [
    ("#faf9f6" in html, "背景色 #faf9f6"),
    ("Noto Serif SC" in html, "字体 Noto Serif SC"),
    ('<link rel="preconnect"' in html, "preconnect 标签"),
    ("fonts.googleapis.com" in html, "Google Fonts link"),
    ("max-width: 800px" in html, "max-width 800px"),
    ("#b30000" in html, "锐评暗红色"),
    ("#fff8dc" in html, "锐评浅黄背景"),
    (".masthead" in html, "Masthead头部"),
    (".article" in html, "Article区块"),
    (".section-header" in html, "Section头部"),
    (".final-section" in html, "终局研判深色区块"),
    (f'{len(core_articles)} 篇核心阵地' if core_articles else None, f"核心阵地文章数: {len(core_articles)}"),
    (f'{len(giants_items)} 条巨头' if giants_items else None, f"巨头绞肉机条数: {len(giants_items)}"),
    (f'{len(radar_items)} 条雷达' if radar_items else None, f"极客雷达条数: {len(radar_items)}"),
]

print("\n🎨 设计规范自检：")
all_pass = True
for cond, name in checks:
    if cond is None:
        continue
    status = "✅" if cond else "❌"
    if not cond:
        all_pass = False
    print(f"  {status} {name}")

if all_pass:
    print("\n✅ 全部检查通过")
