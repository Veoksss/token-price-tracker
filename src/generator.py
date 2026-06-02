"""HTML 生成器 — Token 价格对比页面"""

import os
from datetime import datetime, timezone

from jinja2 import Environment, FileSystemLoader

from src.models import ModelPrice

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "..", "templates")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "output")


def _format_number(value: int) -> str:
    """格式化大数字，如 131072 → '131K' """
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    if value >= 1_000:
        return f"{value / 1_000:.0f}K"
    return str(value)


def _build_arbitrage_examples(models: list[ModelPrice]) -> list[dict]:
    """生成国产 vs 海外套利对比示例。"""
    # 找出国产模型和对应的海外同级别模型
    cn_models = [m for m in models if "🇨🇳" in m.provider_label and m.input_price_usd > 0]
    us_models = [m for m in models if "🇺🇸" in m.provider_label and m.input_price_usd > 0]

    examples = []
    pairs = [
        ("deepseek", "openai"),
        ("qwen", "google"),
        ("kimi", "anthropic"),
    ]

    for cn_provider, us_provider in pairs:
        cn_list = [m for m in cn_models if m.provider == cn_provider]
        us_list = [m for m in us_models if m.provider == us_provider]
        if cn_list and us_list:
            cn_avg = sum(m.input_price_usd for m in cn_list[:5]) / min(len(cn_list), 5)
            us_avg = sum(m.input_price_usd for m in us_list[:5]) / min(len(us_list), 5)
            if us_avg > 0 and cn_avg > 0:
                ratio = round(us_avg / cn_avg, 1)
                if ratio >= 2:
                    examples.append({
                        "cn_model": cn_list[0].display_name,
                        "us_model": us_list[0].display_name,
                        "ratio": ratio,
                    })

    return examples[:5]


def generate_html(
    focus_models: list[ModelPrice],
    all_models: list[ModelPrice],
    changes: list[dict],
    stats: dict,
    output_dir: str = OUTPUT_DIR,
) -> str:
    """生成 Token 价格对比页面。

    Args:
        focus_models: 筛选后的重点模型（展示在表格中）
        all_models: 全量模型数据（用于计算套利示例）
        changes: 价格变动列表
        stats: 预计算的统计数据
        output_dir: 输出目录

    Returns:
        生成的 HTML 文件路径
    """
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    env.filters["format_number"] = _format_number
    template = env.get_template("index.html.j2")

    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y-%m-%d")

    html = template.render(
        date=date_str,
        total_models=len(focus_models),
        models=focus_models,
        changes=changes,
        stats=stats,
        arbitrage_examples=_build_arbitrage_examples(all_models),
    )

    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "index.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    return output_path
