#!/usr/bin/env python3
"""
Feishu Card Sender via AI晨报 Webhook
用法: python3 send_feishu_card.py <card_json_file> [card_json_file2 ...]
"""
import sys
import requests
import json
from pathlib import Path

WEBHOOK_URL = "https://open.feishu.cn/open-apis/bot/v2/hook/eceaf42e-66a4-4db5-ac69-1125197dace9"

def send_card(card_file: str) -> bool:
    """发送单张卡片到 AI晨报 webhook"""
    with open(card_file, 'r', encoding='utf-8') as f:
        card_data = json.load(f)
    
    payload = {
        "msg_type": "interactive",
        "card": card_data
    }
    
    resp = requests.post(WEBHOOK_URL, json=payload, timeout=30)
    result = resp.json()
    
    if result.get("code") == 0:
        print(f"✅ {card_file} 发送成功")
        return True
    else:
        print(f"❌ {card_file} 发送失败: {result}")
        return False

def send_cards(card_files: list) -> bool:
    """批量发送多张卡片"""
    results = []
    for f in card_files:
        if not Path(f).exists():
            print(f"❌ 文件不存在: {f}")
            results.append(False)
            continue
        results.append(send_card(f))
    
    if all(results):
        print(f"\n🎉 全部 {len(results)} 张卡片发送成功")
        return True
    else:
        print(f"\n⚠️ {sum(results)}/{len(results)} 张卡片发送成功")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    success = send_cards(sys.argv[1:])
    sys.exit(0 if success else 1)
