#!/usr/bin/env python3
"""
顺序版：抓取全部 RSS 源 + Firebase/官方 API 补充 + Jina 提取

改进点（2026-03-23）：
- HN 走 Firebase API，零 Jina 消耗
- arXiv 走官方 API，含完整摘要
- Jina 只处理其他 RSS 源
"""
import json
import os
import sys
import time
import requests
import feedparser
import concurrent.futures
import threading
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from morning_brief import RSS_SOURCES, extract_with_jina, RECENCY_BAN_KEYWORDS
from fetch_hn_firebase import fetch_hn_stories_as_entries
from fetch_arxiv import fetch_arxiv_as_entries

DATA_DIR = "/Users/dolan/.openclaw/agents/bibi-agent/data"
os.makedirs(DATA_DIR, exist_ok=True)

ARTICLES = []
TOTAL = 0
articles_lock = threading.Lock()


def fetch_single_feed(source_conf):
    """抓取单个 RSS 源（排除 HN，HN 已走 Firebase）"""
    if isinstance(source_conf, dict):
        source_url = source_conf["url"]
        source_name = source_conf.get("name", source_conf["url"].split('/')[-1])
        weight = source_conf.get("weight", 3)
    else:
        source_url = source_conf
        source_name = source_url.split('/')[-1]
        weight = 3

    # 跳过 HN RSS（已走 Firebase API）
    if 'news.ycombinator.com/rss' in source_url:
        return (source_name, 0, [])

    try:
        feed = feedparser.parse(source_url)
        entries = []
        for entry in feed.entries:
            if not hasattr(entry, 'link'):
                continue
            pub_date = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                try:
                    pub_date = datetime(*entry.published_parsed[:6])
                except:
                    pass
            elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                try:
                    pub_date = datetime(*entry.updated_parsed[:6])
                except:
                    pass

            title = getattr(entry, 'title', '') or ''
            link = entry.link
            combined = (title + ' ' + link).lower()
            is_banned = any(kw.lower() in combined for kw in RECENCY_BAN_KEYWORDS)

            yt_desc = None
            try:
                if hasattr(entry, 'media_description') and entry.media_description:
                    yt_desc = entry.media_description[:3000]
            except:
                pass

            entries.append({
                'url': link,
                'title': title,
                'pub_date': pub_date.isoformat() if pub_date else None,
                'is_banned': is_banned,
                'source': source_name,
                'weight': weight,
                'yt_description': yt_desc,
            })
        return (source_name, len(entries), entries)
    except Exception as e:
        print(f"  ⚠️ {source_name} 失败: {e}")
        return (source_name, 0, [])


def extract_one(entry):
    """
    内容提取：三级分级
    1. HN Firebase → 已有元数据，跳过 Jina
    2. arXiv → 已有摘要，跳过 Jina
    3. 其他 → Jina 提取
    """
    # HN Firebase：直接使用元数据
    if entry.get('_is_hn_firebase'):
        content = (
            f"[HN Discussion]\n\n"
            f"Title: {entry['title']}\n"
            f"URL: {entry['url']}\n"
            f"Score: {entry.get('score', 0)} points | "
            f"Comments: {entry.get('descendants', 0)} | "
            f"by {entry.get('by', 'unknown')}\n"
            f"Discussion: {entry.get('hn_url', entry['url'])}"
        )
        return {
            'content': content,
            'title': entry['title'],
            'age_days': entry.get('age_days', 999),
            'url': entry['url'],
            'weight': entry.get('weight', 4),
            'source': entry.get('source', 'Hacker News'),
            'is_youtube': False,
        }

    # arXiv：使用摘要
    if entry.get('_is_arxiv'):
        authors_str = ', '.join(entry.get('authors', [])[:3])
        content = (
            f"[arXiv Paper]\n\n"
            f"Title: {entry['title']}\n"
            f"Authors: {authors_str}\n"
            f"Categories: {', '.join(entry.get('categories', []))}\n"
            f"URL: {entry['url']}\n\n"
            f"Abstract:\n{entry.get('summary', entry.get('_abstract_preview', ''))}"
        )
        return {
            'content': content,
            'title': entry['title'],
            'age_days': entry.get('age_days', 999),
            'url': entry['url'],
            'weight': entry.get('weight', 4),
            'source': entry.get('source', 'arXiv AI/ML'),
            'is_youtube': False,
        }

    # YouTube：使用 RSS description
    is_youtube = 'youtube.com' in entry['url'] or 'youtu.be' in entry['url']
    if is_youtube and entry.get('yt_description'):
        content = f"[YouTube 视频描述]\n\n{entry['yt_description']}"
    else:
        content = extract_with_jina(entry['url'])

    if content:
        return {
            'content': content,
            'title': entry['title'],
            'age_days': entry.get('age_days', 999),
            'url': entry['url'],
            'weight': entry.get('weight', 1),
            'source': entry.get('source', ''),
            'is_youtube': is_youtube,
        }
    return None


def main():
    global ARTICLES, TOTAL

    print("=" * 60)
    print("📡 Phase 0: HN Firebase API（零 Jina 消耗）")
    print("=" * 60)
    hn_entries = fetch_hn_stories_as_entries(limit=30)
    print(f"  → HN Firebase 获取 {len(hn_entries)} 条\n")

    print("=" * 60)
    print("📚 Phase 0b: arXiv 官方 API（零 Jina 消耗）")
    print("=" * 60)
    arxiv_entries = fetch_arxiv_as_entries(limit=15)
    print(f"  → arXiv 获取 {len(arxiv_entries)} 条\n")

    print("=" * 60)
    print("📡 Phase 1: RSS 源抓取")
    print("=" * 60)

    all_entries = list(hn_entries) + list(arxiv_entries)

    for src in RSS_SOURCES:
        source_name, count, entries = fetch_single_feed(src)
        if count > 0:
            all_entries.extend(entries)
            print(f"  📡 {source_name}: {count} 条")
        time.sleep(0.3)  # 礼貌性延迟

    print(f"\n  📊 共获取 {len(all_entries)} 个条目（含 HN+arXiv）")

    # 时效性过滤
    now = datetime.now()
    valid = []
    for e in all_entries:
        if e.get('is_banned'):
            e['age_days'] = None
            e['demoted'] = True
            continue
        if e.get('pub_date'):
            try:
                pub_dt = datetime.fromisoformat(e['pub_date'])
                age_days = (now - pub_dt).days
                e['age_days'] = age_days
                max_allowed = 30 if e.get('weight', 3) >= 4 else 14
                e['demoted'] = age_days > max_allowed
            except:
                e['age_days'] = 999
                e['demoted'] = True
        else:
            e['age_days'] = 999
            e['demoted'] = True
        valid.append(e)

    valid_count = sum(1 for v in valid if not v.get('demoted'))
    demoted_count = sum(1 for v in valid if v.get('demoted'))
    print(f"  ✅ 有效: {valid_count} | 降权待用: {demoted_count}")

    # 按权重排序
    valid.sort(key=lambda e: (e.get('weight', 1), e.get('age_days', 999)), reverse=True)

    # 全局上限 200 篇
    MAX_TOTAL = 200
    if len(valid) > MAX_TOTAL:
        print(f"  ⚠️ 超出上限，保留前 {MAX_TOTAL} 条（按权重）")
        valid = valid[:MAX_TOTAL]

    TOTAL = len(valid)
    print(f"  🎯 最终处理: {TOTAL} 篇")

    # 第二阶段：分级提取
    ARTICLES = []
    done_count = 0

    # 统计需要 Jina 的数量
    need_jina = sum(
        1 for e in valid
        if not e.get('_is_hn_firebase') and not e.get('_is_arxiv')
    )
    print(f"\n🔥 Phase 2: 分级内容提取")
    print(f"  → HN Firebase: {sum(1 for e in valid if e.get('_is_hn_firebase'))} 条（跳过 Jina）")
    print(f"  → arXiv: {sum(1 for e in valid if e.get('_is_arxiv'))} 条（跳过 Jina）")
    print(f"  → 其他: {need_jina} 条（Jina 提取）")

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_entry = {executor.submit(extract_one, entry): entry for entry in valid}
        for future in concurrent.futures.as_completed(future_to_entry):
            result = future.result()
            with articles_lock:
                if result:
                    ARTICLES.append(result)
                    done_count += 1
                    if done_count % 10 == 0 or done_count == TOTAL:
                        print(f"  进度: {done_count}/{TOTAL} (成功 {len(ARTICLES)})")

    print(f"\n  📊 最终: {len(ARTICLES)} 篇有效文章")

    out_path = os.path.join(DATA_DIR, "raw_rss.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(ARTICLES, f, ensure_ascii=False, indent=2)
    print(f"  💾 写入 {out_path}")

    return len(ARTICLES)


if __name__ == "__main__":
    count = main()
    print(f"\n✅ 完成，{count} 篇文章已写入 raw_rss.json")
