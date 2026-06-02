"""Token 价格追踪 — 主入口

每天运行一次：
1. 从 OpenRouter API 抓取 340+ 模型定价
2. 与历史数据对比，检测价格变动
3. 筛选重点模型，计算套利机会
4. 生成 HTML 对比页面
5. 保存历史数据
"""

import asyncio
import os
import sys
from datetime import datetime, timezone

import httpx

from src.fetchers.openrouter import fetch_openrouter
from src.processor import (
    filter_top_models,
    detect_changes,
    update_history,
    load_history,
)
from src.generator import generate_html


async def main():
    print("=" * 50)
    print(f"🪙 Token Price Tracker — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 50)

    # 1. 抓取
    print("\n📡 [1/4] 从 OpenRouter API 抓取...")
    try:
        all_models = await fetch_openrouter()
        print(f"  ✅ 获取 {len(all_models)} 个模型定价")
    except Exception as e:
        print(f"  ❌ 抓取失败: {e}")
        sys.exit(1)

    # 2. 筛选
    print(f"\n🔍 [2/4] 筛选重点模型...")
    focus_models = filter_top_models(all_models, max_per_category=80)
    print(f"  ✅ 保留 {len(focus_models)} 个重点模型")

    # 3. 检测变动
    print(f"\n📊 [3/4] 检测价格变动...")
    history = load_history()
    changes = detect_changes(focus_models, history)
    if changes:
        print(f"  📢 发现 {len(changes)} 个价格变动！")
        for c in changes:
            direction = "📈 涨价" if c["direction"] == "up" else "📉 降价"
            print(f"    {direction} {c['name'][:40]}: ${c['old_input']:.4f} → ${c['new_input']:.4f}")
    else:
        print(f"  ✅ 无价格变动")
    update_history(focus_models)

    # 4. 计算统计（用全量数据算套利和价差）
    print(f"\n📊 [4/4] 计算统计 + 生成页面...")
    stats = _compute_stats(all_models)

    # 5. 生成页面
    html_path = generate_html(focus_models, all_models, changes, stats)
    print(f"  ✅ {html_path}")

    # 汇总
    cn_count = sum(1 for m in focus_models if "🇨🇳" in m.provider_label)
    free_count = sum(1 for m in focus_models if m.is_free)
    print("\n" + "=" * 50)
    print(f"📊 汇总: {len(focus_models)} 模型 | {cn_count} 国产 | {free_count} 免费")
    print(f"💰 国产均价: ${stats['cn_avg_input']:.4f}/M | 美国均价: ${stats['us_avg_input']:.4f}/M")
    print(f"📈 价差: {stats['cn_vs_us_ratio']}x")
    print("=" * 50)


def _compute_stats(all_models):
    """从全量数据计算统计指标。"""
    cn_inputs = [m.input_price_usd for m in all_models
                 if "🇨🇳" in m.provider_label and m.input_price_usd > 0]
    us_inputs = [m.input_price_usd for m in all_models
                 if "🇺🇸" in m.provider_label and m.input_price_usd > 0]

    cn_avg = sum(cn_inputs) / len(cn_inputs) if cn_inputs else 0
    us_avg = sum(us_inputs) / len(us_inputs) if us_inputs else 0
    ratio = round(us_avg / cn_avg, 1) if cn_avg > 0 else 0

    cheapest = min((m for m in all_models if m.input_price_usd > 0),
                   key=lambda m: m.input_price_usd, default=None)

    return {
        "cheapest_input": f"${cheapest.input_price_usd:.4f}" if cheapest else "N/A",
        "cn_model_count": len(cn_inputs),
        "free_model_count": sum(1 for m in all_models if m.is_free),
        "cn_avg_input": cn_avg,
        "us_avg_input": us_avg,
        "cn_vs_us_ratio": ratio,
    }


if __name__ == "__main__":
    asyncio.run(main())
