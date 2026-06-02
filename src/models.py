"""Token 价格追踪 — 数据模型"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class ModelPrice:
    """归一化后的模型定价数据"""

    model_id: str                    # e.g. "deepseek/deepseek-chat"
    display_name: str                # e.g. "DeepSeek V3"
    provider: str                    # e.g. "deepseek", "openai", "anthropic"
    provider_label: str = ""         # 中文标签

    input_price_usd: float = 0.0     # USD per 1M tokens
    output_price_usd: float = 0.0

    context_window: int = 0
    max_output_tokens: int = 0

    is_free: bool = False
    category: str = "other"          # llm / vision / code / video / audio

    source: str = "openrouter"       # openrouter / official
    source_url: str = ""

    updated_at: str = ""             # ISO date string


# 提供商中文标签
PROVIDER_LABELS: dict[str, str] = {
    "deepseek": "深度求索 🇨🇳",
    "qwen": "通义千问 🇨🇳",
    "kimi": "月之暗面 🇨🇳",
    "zhipu": "智谱 AI 🇨🇳",
    "minimax": "MiniMax 🇨🇳",
    "stepfun": "阶跃星辰 🇨🇳",
    "baichuan": "百川智能 🇨🇳",
    "01-ai": "零一万物 🇨🇳",
    "openai": "OpenAI 🇺🇸",
    "anthropic": "Anthropic 🇺🇸",
    "google": "Google 🇺🇸",
    "meta": "Meta 🇺🇸",
    "mistral": "Mistral 🇫🇷",
    "cohere": "Cohere 🇨🇦",
    "x-ai": "xAI 🇺🇸",
    "amazon": "Amazon 🇺🇸",
    "nvidia": "NVIDIA 🇺🇸",
    "microsoft": "Microsoft 🇺🇸",
}

# 分类关键词
CATEGORY_KEYWORDS = {
    "vision": ["vision", "vl", "visual", "image", "video", "sight"],
    "code": ["coder", "code", "programming"],
    "video": ["video-gen", "video", "animate", "kling"],
    "audio": ["audio", "speech", "tts", "whisper", "voice"],
}


def categorize(model_id: str) -> str:
    """根据模型 ID 自动分类。"""
    lower = model_id.lower()
    for cat, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in lower:
                return cat
    return "llm"
