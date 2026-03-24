#!/usr/bin/env python3
"""
Feishu Card Sender for Dolan's Morning Brief
用法: python3 send_feishu_card.py [brief_file]
如果不带参数，默认读取 data/brief_content.txt
"""
import sys
import os
import re
import json
import requests
from datetime import date
from pathlib import Path

WEBHOOK_URL = "https://open.feishu.cn/open-apis/bot/v2/hook/eceaf42e-66a4-4db5-ac69-1125197dace9"

def get_github_url():
    """从 data/ 目录找到最新的 daily_brief HTML 文件，构建 GitHub Pages URL"""
    data_dir = Path(__file__).parent.parent / "data"
    today = date.today()
    date_str = today.strftime("%Y-%m-%d")
    
    # 优先找今天的文件
    candidates = [
        f"daily_brief_{date_str}.html",
        f"daily_brief_{date_str.replace('-', '')}.html",
    ]
    
    for c in candidates:
        p = data_dir / c
        if p.exists():
            filename = p.name
            break
    else:
        # 找不到就用当天日期命名
        filename = f"daily_brief_{date_str}.html"
    
    return f"https://dolan9644.github.io/bibi-intel/{filename}"

def extract_sections(brief_text: str) -> dict:
    """从 brief_content.txt 提取4个板块的内容摘要"""
    sections = {
        "核心阵地": "",
        "巨头绞肉机": "",
        "极客雷达": "",
        "终局研判": ""
    }
    
    current = None
    lines = brief_text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith('🎯') or '核心阵地' in line:
            current = "核心阵地"
            continue
        elif line.startswith('🌍') or '巨头绞肉机' in line:
            current = "巨头绞肉机"
            continue
        elif line.startswith('📡') or '极客雷达' in line:
            current = "极客雷达"
            continue
        elif line.startswith('💡') or '终局研判' in line:
            current = "终局研判"
            continue
        elif line.startswith('##') and '锐评' in line:
            # 忽略 Dolan's 锐评 的单独出现（合并到板块）
            continue
        
        if current and line:
            if sections[current]:
                sections[current] += "；" + line
            else:
                sections[current] = line
    
    # 清理：去掉标题行、Dolan's 锐评 单独段落、原文链接等
    for k in sections:
        sections[k] = re.sub(r'\[.*?\]\(.*?\)', '', sections[k])  # 去掉 markdown 链接
        sections[k] = re.sub(r'https?://\S+', '', sections[k])  # 去掉 URL
        sections[k] = re.sub(r'Dolan.*锐评[：:]?', '', sections[k])  # 去掉 Dolan's 锐评
        sections[k] = sections[k].strip('：:、。 ')
        # 截断过长内容
        if len(sections[k]) > 300:
            sections[k] = sections[k][:300] + "..."
    
    return sections

def get_topic_from_brief(brief_text: str) -> str:
    """从 brief 提取副标题主题"""
    lines = brief_text.split('\n')
    for line in lines:
        if line.startswith('Title:'):
            return line.replace('Title:', '').strip()
    # 如果找不到 Title，取第一行非空内容
    for line in lines[:10]:
        if line.strip() and not line.startswith('#') and len(line.strip()) > 10:
            return line.strip()[:50]
    return ""

def build_card(date_str: str, topic: str, sections: dict, github_url: str) -> dict:
    """构建飞书卡片 JSON"""
    body = f"**🎯 核心阵地**\n{sections.get('核心阵地', '（今日无内容）')}\n\n"
    body += f"**🌍 巨头绞肉机**\n{sections.get('巨头绞肉机', '（今日无内容）')}\n\n"
    body += f"**📡 极客雷达**\n{sections.get('极客雷达', '（今日无内容）')}\n\n"
    body += f"**💡 终局研判**\n{sections.get('终局研判', '（今日无内容）')}\n\n"
    body += f"📖 **完整阅读**：{github_url}"
    
    return {
        "msg_type": "interactive",
        "card": {
            "config": {"wide_screen_mode": True},
            "header": {
                "title": {"tag": "plain_text", "content": f"📰 DOLAN'S 全景内参 · {date_str}"},
                "subtitle": {"tag": "plain_text", "content": topic[:80] if topic else "智能体与算力的最新战场"},
                "template": "red"
            },
            "elements": [
                {"tag": "markdown", "content": body}
            ]
        }
    }

def send_card(card_data: dict) -> bool:
    """发送卡片到 AI晨报 webhook"""
    try:
        resp = requests.post(WEBHOOK_URL, json=card_data, timeout=30)
        result = resp.json()
        if result.get("code") == 0:
            print(f"✅ 卡片发送成功")
            return True
        else:
            print(f"❌ 发送失败: {result}")
            return False
    except Exception as e:
        print(f"❌ 发送异常: {e}")
        return False

def main():
    # 确定 brief 文件路径
    if len(sys.argv) > 1:
        brief_file = sys.argv[1]
    else:
        script_dir = Path(__file__).parent
        today = date.today()
        brief_file = script_dir.parent / "data" / "brief_content.txt"
        
        # 尝试带日期的版本
        date_brief = script_dir.parent / "data" / f"brief_content_{today.strftime('%Y-%m-%d')}.txt"
        if date_brief.exists():
            brief_file = date_brief
    
    if not Path(brief_file).exists():
        print(f"❌ brief 文件不存在: {brief_file}")
        sys.exit(1)
    
    print(f"📖 读取 brief 文件: {brief_file}")
    with open(brief_file, 'r', encoding='utf-8') as f:
        brief_text = f.read()
    
    # 提取信息
    today_str = date.today().strftime("%Y-%m-%d")
    topic = get_topic_from_brief(brief_text)
    sections = extract_sections(brief_text)
    github_url = get_github_url()
    
    print(f"📅 日期: {today_str}")
    print(f"📌 主题: {topic}")
    print(f"🔗 GitHub: {github_url}")
    print(f"📦 板块: {list(sections.keys())}")
    
    # 构建卡片
    card = build_card(today_str, topic, sections, github_url)
    
    # 发送
    success = send_card(card)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
