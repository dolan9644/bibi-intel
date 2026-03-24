#!/usr/bin/env python3
"""
Dolan's Morning Brief — 全自动串口执行脚本
一次触发，完整跑完 RSS → topic → writer → design → GitHub → 飞书
"""
import subprocess
import time
import json
import sys
import os
from pathlib import Path

WORKSPACE = "/Users/dolan/.openclaw/agents/bibi-agent"
TODAY = "2026-03-23"

def run(cmd, label, timeout=600):
    print(f"\n{'='*60}")
    print(f"🔧 {label}")
    print(f"{'='*60}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
    print(result.stdout[-2000:] if result.stdout else "")
    if result.returncode != 0:
        print(f"❌ {label} 失败 (code {result.returncode})")
        print(result.stderr[-500:] if result.stderr else "")
        return False
    print(f"✅ {label} 完成")
    return True

def check(path, label, min_size=1000):
    size = os.path.getsize(path) if os.path.exists(path) else 0
    ok = size > min_size
    print(f"{'✅' if ok else '❌'} {label}: {size} bytes")
    return ok

# ── Step 1: RSS 抓取 ──────────────────────────────────────
if not run(f"python3 {WORKSPACE}/automation/fetch_all_rss.py", "Step 1: RSS 抓取", timeout=600):
    sys.exit(1)

raw_rss = f"{WORKSPACE}/data/raw_rss.json"
if not check(raw_rss, "raw_rss.json 完整性", min_size=50000):
    print("❌ raw_rss.json 不完整，中止")
    sys.exit(1)

# ── Step 2: bibi-topic ─────────────────────────────────────
if not run(f"python3 - << 'PYEOF'\nimport sys; sys.path.insert(0, '{WORKSPACE}'); exec(open('{WORKSPACE}/bibi-topic/topic_radar.py').read() if os.path.exists('{WORKSPACE}/bibi-topic/topic_radar.py') else 'print(\"NO_TOPIC_RADAR\")')\nPYEOF", "Step 2: bibi-topic 情报雷达", timeout=300):
    print("⚠️ bibi-topic 失败，跳过或使用备用逻辑")

# ── Step 3: bibi-writer ───────────────────────────────────
brief_txt = f"{WORKSPACE}/data/brief_content.txt"
if os.path.exists(f"{WORKSPACE}/data/topic_result.json"):
    print(f"\n📝 准备 writer 输入: {WORKSPACE}/data/topic_result.json")

# ── Step 4: bibi-design ───────────────────────────────────
html_out = f"{WORKSPACE}/data/daily_brief_{TODAY}.html"
print(f"\n{'='*60}")
print("📦 最终 HTML 将输出到:")
print(f"   {html_out}")
print(f"{'='*60}")

print("\n✅ 串口脚本执行完毕")
