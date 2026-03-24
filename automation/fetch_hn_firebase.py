#!/usr/bin/env python3
"""
Hacker News Firebase API Fetcher
官方 API，零成本，零 429 风险，稳定直连

API: https://hacker-news.firebaseio.com/v0/topstories.json
"""
import os
import sys
import json
import time
import httpx
from datetime import datetime
from typing import List, Dict, Optional

# 复用主脚本的 RECENCY_BAN_KEYWORDS
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from morning_brief import RECENCY_BAN_KEYWORDS
except ImportError:
    RECENCY_BAN_KEYWORDS = []

import os


def fetch_hn_stories(limit: int = 30) -> List[Dict]:
    """
    通过 Firebase API 获取 HN Top Stories
    
    Args:
        limit: 获取条数（默认30条）
    Returns:
        HN 故事列表，每条含 title/url/score/by/time
    """
    print(f"  → HN Firebase API: 获取 top {limit} 条...")
    
    stories = []
    
    try:
        # 1. 获取 top story IDs
        with httpx.Client(timeout=15) as client:
            resp = client.get("https://hacker-news.firebaseio.com/v0/topstories.json")
            story_ids = resp.json()[:limit]
        
        # 2. 批量获取每个 story 详情（串行，有礼貌延迟）
        for i, sid in enumerate(story_ids):
            try:
                with httpx.Client(timeout=10) as client:
                    item_resp = client.get(f"https://hacker-news.firebaseio.com/v0/item/{sid}.json")
                    item = item_resp.json()
                
                if not item or item.get("type") != "story":
                    continue
                
                title = item.get("title", "")
                url = item.get("url") or f"https://news.ycombinator.com/item?id={sid}"
                score = item.get("score", 0)
                by = item.get("by", "unknown")
                descendants = item.get("descendants", 0)
                time_ts = item.get("time", 0)
                
                # 时间转换
                pub_date = datetime.fromtimestamp(time_ts) if time_ts else None
                
                # 检查 banned 关键词
                combined = (title + ' ' + url).lower()
                is_banned = any(kw.lower() in combined for kw in RECENCY_BAN_KEYWORDS)
                
                stories.append({
                    "id": sid,
                    "title": title,
                    "url": url,
                    "score": score,
                    "by": by,
                    "descendants": descendants,
                    "hn_url": f"https://news.ycombinator.com/item?id={sid}",
                    "pub_date": pub_date.isoformat() if pub_date else None,
                    "age_days": (datetime.now() - pub_date).days if pub_date else 999,
                    "is_banned": is_banned,
                    "source": "Hacker News",
                    "weight": 4,
                })
                
                if (i + 1) % 10 == 0:
                    print(f"    HN 进度: {i+1}/{len(story_ids)}")
                
                time.sleep(0.3)  # 礼貌性延迟，不冲击 API
                
            except Exception as e:
                print(f"    ⚠️ HN story {sid} 失败: {e}")
                continue
    
    except Exception as e:
        print(f"  ⚠️ HN Firebase API 失败: {e}")
    
    success = len(stories)
    valid = sum(1 for s in stories if not s.get("is_banned"))
    print(f"  ✅ HN 完成: {success} 条获取, {valid} 条有效")
    
    return stories


def fetch_hn_stories_as_entries(limit: int = 30) -> List[Dict]:
    """
    返回格式兼容 fetch_all_rss.py 的 extract_one()
    用于直接替换 Jina 提取阶段的 HN 条目
    """
    stories = fetch_hn_stories(limit)
    entries = []
    
    for s in stories:
        entries.append({
            "url": s["url"],
            "title": s["title"],
            "pub_date": s["pub_date"],
            "age_days": s.get("age_days", 999),
            "is_banned": s.get("is_banned", False),
            "source": "Hacker News",
            "weight": 4,
            "hn_url": s.get("hn_url", ""),
            "score": s.get("score", 0),
            "by": s.get("by", ""),
            "descendants": s.get("descendants", 0),
            # 特殊标记：走 Jina 降级时不重复抓 HN
            "_is_hn_firebase": True,
        })
    
    return entries


if __name__ == "__main__":
    stories = fetch_hn_stories(20)
    print(f"\n{'='*60}")
    for i, s in enumerate(stories[:5], 1):
        print(f"{i}. {s['title']}")
        print(f"   ⬆ {s['score']} | 💬 {s['descendants']} | by {s['by']}")
        print(f"   🔗 {s['url']}")
    print(f"\n共 {len(stories)} 条 HN 故事")
