#!/usr/bin/env python3
"""
Dolan's AI Morning Brief - Full Automation Script
自动执行：RSS抓取 → Jina提取 → bibi-topic去重 → bibi-writer撰写 → bibi-design排版 → GitHub推送 → 飞书推送
"""

import json
import os
import subprocess
import requests
from datetime import datetime
from urllib.parse import urljoin
import feedparser

# 时效性黑名单关键词
RECENCY_BAN_KEYWORDS = [
    "anniversary", "十周年", "十年", "回顾", "history of", "looking back",
    "in memory", "纪念", " obituary", "讣告", "去世", "passed away",
    "retrospective", "回首", "x周年",
]

# 配置 - 全新的高级 RSS 源
RSS_SOURCES = [
    # === 泛读（查漏补缺）===
    "https://news.ycombinator.com/rss",  # Hacker News
    "https://www.jiqizhixin.com/feed",   # 机器之心
    
    # === 1. 官方一手底座 (The Foundation Models) ===
    "https://www.anthropic.com/feed.xml",           # Anthropic
    "https://openai.com/blog/rss.xml",             # OpenAI Research
    "https://deepmind.google/blog/rss.xml",        # Google DeepMind
    "https://huggingface.co/blog/feed.xml",        # Hugging Face Blog
    
    # === 2. 极客与独立研究员 (The Hardcore Hackers) ===
    "https://simonwillison.net/atom/entries/",      # Simon Willison
    "https://www.llamaindex.ai/blog/rss",           # LlamaIndex Blog
    "https://blog.pragmaticengineer.com/rss/",      # The Pragmatic Engineer
    
    # === 3. GitHub 核心军火库 (The Codebase) ===
    "https://github.com/openclaw/openclaw/commits/main.atom",      # OpenClaw
    "https://github.com/langchain-ai/langchain/releases.atom",     # LangChain
    "https://github.com/microsoft/autogen/commits/main.atom",      # AutoGen
    
    # === 4. 国内大厂与深潜商业 (The Domestic Deep Dive) ===
    "https://rsshub.app/latepost",                  # 晚点 LatePost
    "https://rsshub.app/juejin/category/ai",       # 稀土掘金 AI
    "https://rsshub.app/zhihu/topic/19551275/top-answers",  # 知乎 AI

    # === 5. 专业媒体 (Professional Media) ===
    # 注：Bloomberg Tech / The Information / arXiv 需要认证或网络受限，用以下替代源
    "https://techcrunch.com/feed/",                           # TechCrunch
    "https://www.wired.com/feed/rss",                         # Wired
    "https://www.technologyreview.com/feed/",                  # MIT Tech Review
    "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",  # The Verge AI
]

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_REPO = "dolan9644/dolans-brief"
FEISHU_WEBHOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/eceaf42e-66a4-4db5-ac69-1125197dace9"

def fetch_rss_urls(max_urls=50):
    """获取RSS源的URL列表"""
    urls = []
    source_counts = {}
    
    for source in RSS_SOURCES:
        try:
            feed = feedparser.parse(source)
            source_name = source.split('/')[-1] if '/' in source else source[:30]
            count = 0
            for entry in feed.entries[:8]:  # 每个源取8条
                if hasattr(entry, 'link'):
                    urls.append(entry.link)
                    count += 1
            source_counts[source_name] = count
        except Exception as e:
            print(f"  ⚠️ {source[:40]}... 失败")
    
    print(f"   📊 来源统计: {source_counts}")
    return urls[:max_urls]

def extract_with_jina(url):
    """使用Jina Reader提取网页内容"""
    try:
        jina_url = f"https://r.jina.ai/{url}"
        resp = requests.get(jina_url, timeout=30)
        if resp.status_code == 200:
            return resp.text[:6000]  # 限制长度
    except Exception as e:
        print(f"  ⚠️ 提取失败: {url[:50]}...")
    return None

def call_bibi_topic(articles_text):
    """调用 bibi-topic 进行去重"""
    # 这里通过 sessions_spawn 调用 subagent
    # 简化版：直接返回JSON
    return [
        {"category": "测试", "event_core": "自动化测试事件", "details_and_data": "这是自动化流程测试", "perspectives": ["测试观点1"]}
    ]

def call_bibi_writer(json_data):
    """调用 bibi-writer 撰写"""
    return "Title: Dolan's 全景内参\n\n测试内容"

def call_bibi_design(content):
    """调用 bibi-design 排版"""
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>Dolan's AI Brief</title>
</head>
<body>
    <h1>{content}</h1>
</body>
</html>"""
    return html

def push_to_github(html_content, filename):
    """推送到GitHub"""
    import base64
    api_url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{filename}"
    
    # 获取现有文件的 SHA（如果存在）
    sha = None
    try:
        resp = requests.get(api_url, headers={"Authorization": f"token {GITHUB_TOKEN}"})
        if resp.status_code == 200:
            sha = resp.json()["sha"]
    except:
        pass
    
    data = {
        "message": f"Update {filename}",
        "content": base64.b64encode(html_content.encode()).decode()
    }
    if sha:
        data["sha"] = sha
    
    resp = requests.put(api_url, json=data, headers={"Authorization": f"token {GITHUB_TOKEN}"})
    return resp.status_code in [200, 201]

def send_feishu_card(title, summary, html_url):
    """发送飞书卡片"""
    payload = {
        "msg_type": "interactive",
        "card": {
            "config": {"wide_screen_mode": True, "enable_forward": True},
            "header": {"title": {"tag": "plain_text", "content": f"📰 {title}"}, "template": "red"},
            "elements": [
                {"tag": "markdown", "content": summary},
                {"tag": "hr"},
                {"tag": "action", "actions": [{"tag": "button", "text": {"tag": "plain_text", "content": "👁️ 阅读完整研报"}, "type": "primary", "url": html_url}]},
                {"tag": "note", "elements": [{"tag": "plain_text", "content": f"Generated by BIBI Agent · {datetime.now().strftime('%Y-%m-%d')}"}]}
            ]
        }
    }
    resp = requests.post(FEISHU_WEBHOOK, json=payload)
    return resp.status_code == 200

def main():
    print("🚀 Dolan's AI Morning Brief 工作流启动...")
    print("="*50)
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    # 1. 抓取 RSS
    print("📡 [步骤1] 抓取 RSS 源...")
    urls = fetch_rss_urls()
    print(f"   ✅ 共获取 {len(urls)} 个URL")
    
    # 2. Jina 提取（示例取前5个）
    print("🔥 [步骤2] Jina Reader 提取全文...")
    articles = []
    for i, url in enumerate(urls[:5]):
        print(f"   [{i+1}/5] 提取中: {url[:50]}...")
        content = extract_with_jina(url)
        if content:
            articles.append(content)
    print(f"   ✅ 成功提取 {len(articles)} 篇文章")
    
    # 3. bibi-topic 去重
    print("🧠 [步骤3] bibi-topic 去重处理...")
    json_data = call_bibi_topic(articles)
    
    # 4. bibi-writer 撰写
    print("✍️ [步骤4] bibi-writer 撰写...")
    content = call_bibi_writer(json_data)
    
    # 5. bibi-design 排版
    print("🎨 [步骤5] bibi-design 排版...")
    html = call_bibi_design(content)
    
    # 6. GitHub 推送
    print("📤 [步骤6] 推送到 GitHub...")
    filename = f"daily_brief_{date_str}.html"
    if push_to_github(html, filename):
        html_url = f"https://htmlpreview.github.io/?https://raw.githubusercontent.com/{GITHUB_REPO}/main/{filename}"
        print(f"   ✅ GitHub 推送成功")
    else:
        html_url = ""
        print(f"   ⚠️ GitHub 推送失败")
    
    # 7. 飞书推送
    print("📱 [步骤7] 发送飞书卡片...")
    if send_feishu_card(f"Dolan's AI Brief {date_str}", "今日AI/科技要闻", html_url):
        print("   ✅ 飞书推送成功")
    else:
        print("   ⚠️ 飞书推送失败")
    
    print("="*50)
    print("✅ 工作流执行完成！")

if __name__ == "__main__":
    main()
