#!/usr/bin/env python3
"""
arXiv AI/ML Paper Fetcher
官方 API，零成本，零 429 风险，稳定直连

API: https://export.arxiv.org/api/query
策略：递进式查询（窄 → 宽 → 最近更新）
"""
import os
import sys
import re
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


def _parse_arxiv_entry(entry_xml: str) -> Optional[Dict]:
    """解析单条 arXiv XML 条目"""
    arxiv_id_match = re.search(r'<id>http://arxiv.org/abs/([^<]+)</id>', entry_xml)
    title_match = re.search(r'<title>(.*?)</title>', entry_xml, re.DOTALL)
    summary_match = re.search(r'<summary>(.*?)</summary>', entry_xml, re.DOTALL)
    published_match = re.search(r'<published>([^<]+)</published>', entry_xml)
    authors = re.findall(r'<name>([^<]+)</name>', entry_xml)
    categories = re.findall(r'<category term="([^"]+)"', entry_xml)
    
    if not arxiv_id_match or not title_match:
        return None
    
    # 清理空白
    raw_summary = summary_match.group(1).strip() if summary_match else ""
    clean_summary = ' '.join(raw_summary.split())
    
    pub_str = published_match.group(1)[:10] if published_match else ""
    try:
        pub_date = datetime.fromisoformat(pub_str)
    except:
        pub_date = None
    
    # 检查 banned 关键词
    title = title_match.group(1).strip().replace('\n', ' ')
    combined = (title + ' ' + clean_summary).lower()
    is_banned = any(kw.lower() in combined for kw in RECENCY_BAN_KEYWORDS)
    
    return {
        "id": arxiv_id_match.group(1),
        "title": title,
        "summary": clean_summary,
        "authors": authors[:3],  # 只取前3个作者
        "published": pub_str,
        "pub_date": pub_date.isoformat() if pub_date else None,
        "age_days": (datetime.now() - pub_date).days if pub_date else 999,
        "categories": categories[:3],
        "is_banned": is_banned,
    }


def _query_arxiv(query: str, sort_by: str, max_results: int) -> List[Dict]:
    """执行单次 arXiv API 查询"""
    url = (
        f"https://export.arxiv.org/api/query"
        f"?search_query={query}"
        f"&start=0"
        f"&max_results={max_results}"
        f"&sortBy={sort_by}"
        f"&sortOrder=descending"
    )
    
    try:
        with httpx.Client(timeout=30) as client:
            resp = client.get(url, headers={"User-Agent": "BIBI-AI-Morning-Brief/1.0"})
            xml = resp.text
        
        if len(xml) < 500:
            return []
        
        # 简单 XML 解析（避免 heavy lxml 依赖）
        entries = re.findall(r'<entry>(.*?)</entry>', xml, re.DOTALL)
        papers = []
        for entry in entries:
            parsed = _parse_arxiv_entry(entry)
            if parsed:
                papers.append(parsed)
        
        return papers
    
    except Exception as e:
        print(f"    ⚠️ arXiv 查询失败: {e}")
        return []


def fetch_arxiv_papers(limit: int = 15) -> List[Dict]:
    """
    获取最新 AI/ML 论文
    递进策略：cs.AI → cs.AI+cs.LG+cs.CL → 最近更新
    """
    print(f"  → arXiv API: 获取 {limit} 篇 AI/ML 论文...")
    
    strategies = [
        ("cat:cs.AI", "submittedDate"),  # 默认：最新 AI 论文
        ("cat:cs.AI+OR+cat:cs.LG+OR+cat:cs.CL", "submittedDate"),  # 扩大：AI + ML + NLP
        ("cat:cs.AI+OR+cat:cs.LG", "lastUpdatedDate"),  # 保底：最近更新的
    ]
    
    for i, (query, sort_by) in enumerate(strategies):
        papers = _query_arxiv(query, sort_by, limit)
        if papers:
            if i > 0:
                print(f"    ✓ 递进策略 #{i+1} 生效，获取 {len(papers)} 篇")
            return papers
        if i < len(strategies) - 1:
            print(f"    ⚠️ 策略 #{i+1} 空，等待 3s 后递进...")
            time.sleep(3)
    
    print(f"    ⚠️ 所有策略均失败")
    return []


def fetch_arxiv_as_entries(limit: int = 15) -> List[Dict]:
    """
    返回格式兼容 fetch_all_rss.py
    """
    papers = fetch_arxiv_papers(limit)
    entries = []
    
    for p in papers:
        abstract_preview = p["summary"][:300] if p["summary"] else ""
        
        entries.append({
            "url": f"https://arxiv.org/abs/{p['id']}",
            "title": p["title"],
            "pub_date": p["pub_date"],
            "age_days": p.get("age_days", 999),
            "is_banned": p.get("is_banned", False),
            "source": "arXiv AI/ML",
            "weight": 4,
            "summary": p["summary"],  # 完整摘要，LLM 上下文
            "authors": p["authors"],
            "categories": p["categories"],
            # 特殊标记：不需要 Jina 提取（有摘要就够了）
            "_is_arxiv": True,
            "_abstract_preview": abstract_preview,
        })
    
    success = len(entries)
    valid = sum(1 for e in entries if not e.get("is_banned"))
    print(f"  ✅ arXiv 完成: {success} 篇获取, {valid} 篇有效")
    
    return entries


if __name__ == "__main__":
    papers = fetch_arxiv_papers(10)
    print(f"\n{'='*60}")
    for i, p in enumerate(papers[:5], 1):
        print(f"{i}. {p['title']}")
        print(f"   👤 {', '.join(p['authors'])}")
        print(f"   📅 {p['published']} | 🏷️ {', '.join(p['categories'])}")
        print(f"   🔗 https://arxiv.org/abs/{p['id']}")
    print(f"\n共 {len(papers)} 篇论文")
