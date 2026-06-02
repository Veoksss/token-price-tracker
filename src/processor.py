"""价格数据处理：筛选、排序、历史对比"""

import json
import os
from datetime import datetime, timezone
from typing import Optional

from src.models import ModelPrice

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
HISTORY_FILE = os.path.join(DATA_DIR, "price_history.json")


def load_history() -> dict[str, list[dict]]:
    """加载历史价格数据。

    Returns:
        {model_id: [{date, input_usd, output_usd}, ...]}
    """
    if not os.path.exists(HISTORY_FILE):
        return {}
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_history(history: dict):
    """保存历史价格数据。"""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def detect_changes(
    current: list[ModelPrice],
    history: dict[str, list[dict]],
) -> list[dict]:
    """对比当前和历史价格，检测变化。

    Returns:
        [{"model_id": str, "name": str, "old_input": float, "new_input": float, ...}]
    """
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    changes = []

    for m in current:
        old_entries = history.get(m.model_id, [])
        if not old_entries:
            continue

        last = old_entries[-1]
        old_in = last.get("input_usd", 0)
        old_out = last.get("output_usd", 0)

        if old_in != m.input_price_usd or old_out != m.output_price_usd:
            direction = "down" if m.input_price_usd < old_in else "up"
            changes.append({
                "model_id": m.model_id,
                "name": m.display_name,
                "provider_label": m.provider_label,
                "old_input": old_in,
                "old_output": old_out,
                "new_input": m.input_price_usd,
                "new_output": m.output_price_usd,
                "direction": direction,
                "date": today,
                "url": m.source_url,
            })

    return changes


def update_history(current: list[ModelPrice]):
    """将当前价格追加到历史记录。"""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    history = load_history()

    for m in current:
        entry = {
            "date": today,
            "input_usd": m.input_price_usd,
            "output_usd": m.output_price_usd,
        }
        if m.model_id not in history:
            history[m.model_id] = []
        # 同一天不重复记录
        if not history[m.model_id] or history[m.model_id][-1]["date"] != today:
            history[m.model_id].append(entry)

    save_history(history)


def filter_top_models(
    models: list[ModelPrice],
    category: Optional[str] = None,
    max_per_category: int = 50,
) -> list[ModelPrice]:
    """筛选重点模型（按类别，每类取最便宜/最重要的一批）。

    Args:
        models: 全部模型
        category: 可选过滤类别
        max_per_category: 每类最多保留
    """
    if category and category != "all":
        models = [m for m in models if m.category == category]

    # 排除一些实验性/废弃模型
    exclude_keywords = ["deprecated", "test", "internal", "draft"]
    models = [
        m for m in models
        if not any(kw in m.model_id.lower() for kw in exclude_keywords)
    ]

    # 按提供商分组，每组保留前几个
    from collections import defaultdict
    by_provider: dict[str, list[ModelPrice]] = defaultdict(list)
    for m in models:
        by_provider[m.provider].append(m)

    result = []
    for provider, provider_models in by_provider.items():
        # 按价格排序（取便宜的优先）
        provider_models.sort(key=lambda m: m.input_price_usd)
        result.extend(provider_models[:10])

    # 额外保留一些免费模型
    free_models = [m for m in models if m.is_free and m not in result]
    result.extend(free_models)

    # 去重
    seen = set()
    unique = []
    for m in result:
        if m.model_id not in seen:
            seen.add(m.model_id)
            unique.append(m)

    # 最终按价格排序
    unique.sort(key=lambda m: m.input_price_usd)
    return unique[:max_per_category]
