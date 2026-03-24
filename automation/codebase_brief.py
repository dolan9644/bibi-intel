#!/usr/bin/env python3
"""
OpenClaw 代码库 24 小时变动简报
每天 23:00 定时运行，收集 openclaw/openclaw 过去 24h 的 PR 合并，
AI 总结后通过飞书 Webhook 推送。
"""

import os
import sys
import json
import subprocess
import requests
from datetime import datetime, timedelta, timezone

REPO = "openclaw/openclaw"
FEISHU_WEBHOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/eceaf42e-66a4-4db5-ac69-1125197dace9"

def get_since_time():
    since = datetime.now(timezone.utc) - timedelta(hours=24)
    return since.isoformat().replace("+00:00", "Z")

def run_cmd(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"⚠️ 命令执行失败: {cmd}")
        print(f"   {e.stderr.strip()}")
        return None

def fetch_prs():
    since_time = get_since_time()
    raw = run_cmd(
        f"gh pr list --repo {REPO} --state=merged --limit=50 "
        f"--json number,title,author,mergedAt,url"
    )
    if not raw:
        return []

    prs = json.loads(raw)
    since_dt = datetime.fromisoformat(since_time.replace("Z", "+00:00"))
    filtered = []
    for pr in prs:
        try:
            merged = datetime.fromisoformat(pr["mergedAt"].replace("Z", "+00:00"))
            if merged > since_dt:
                filtered.append(pr)
        except Exception:
            pass
    return filtered

def build_pr_list(prs):
    """生成纯 PR 标题列表，供 AI 总结用"""
    lines = []
    for pr in prs:
        author = pr.get("author", {}).get("login", "unknown")
        lines.append(f"[{pr['title']}] (@{author})")
    return "\n".join(lines)

def ai_summarize(pr_list_text):
    """生成 PR 列表文件，供上层 agent 调用 sub-agent 总结"""
    # 保存到 /tmp/ 供 bibi-agent 读取并调用 sub-agent 总结
    out_path = "/tmp/codebase_pr_list.txt"
    with open(out_path, "w") as f:
        f.write(pr_list_text)
    print(f"   PR 列表已写入 {out_path}，供 AI 总结使用")
    return None  # 由 bibi-agent 自行调用 sub-agent 总结

def push_feishu(text):
    try:
        resp = requests.post(
            FEISHU_WEBHOOK,
            json={"msg_type": "text", "content": {"text": text}},
            timeout=10,
        )
        resp.raise_for_status()
        print("✅ 飞书推送成功")
        return True
    except Exception as e:
        print(f"⚠️ 飞书推送失败: {e}")
        return False

def main():
    print(f"⏳ 开始抓取 OpenClaw 过去 24h 变动...")

    prs = fetch_prs()
    print(f"   获取到 {len(prs)} 个合并 PR")

    if not prs:
        print("📭 过去 24h 无合并 PR，静默退出。")
        sys.exit(0)

    pr_text = build_pr_list(prs)

    print("🤖 调用 AI 生成自然语言简报...")
    summary = ai_summarize(pr_text)

    today = datetime.now().strftime("%Y-%m-%d")
    header = f"🌙 OpenClaw 代码日报 — {today}（{len(prs)} 个合并）\n"

    if summary:
        full = header + summary
    else:
        # fallback：直接列标题
        items = [f"• {p['title']} (@{p.get('author',{}).get('login','')})" for p in prs]
        full = header + "\n".join(items)

    print("\n" + "=" * 50)
    print(full)
    print("=" * 50)

    # 注：不直接 push，由 bibi-agent 读取 /tmp/codebase_pr_list.txt
    # 然后自行调用 sub-agent 总结，最后 push 到飞书

if __name__ == "__main__":
    main()
