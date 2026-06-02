"""OpenRouter API 抓取器 — Token 价格追踪的核心数据源

OpenRouter 公开 API 返回 340+ 模型的定价、上下文窗口等信息。
无需 API Key 即可访问模型列表端点。
"""

from datetime import datetime, timezone
from typing import Optional

import httpx

from src.models import ModelPrice, PROVIDER_LABELS, categorize

OPENROUTER_API = "https://openrouter.ai/api/v1/models"

# 提取 provider 名的映射
PROVIDER_MAP = {
    "deepseek": "deepseek",
    "qwen": "qwen",
    "moonshot": "kimi",
    "zhipu": "zhipu",
    "minimax": "minimax",
    "stepfun": "stepfun",
    "01-ai": "01-ai",
    "openai": "openai",
    "anthropic": "anthropic",
    "google": "google",
    "meta-llama": "meta",
    "mistralai": "mistral",
    "cohere": "cohere",
    "x-ai": "x-ai",
    "amazon": "amazon",
    "nvidia": "nvidia",
    "microsoft": "microsoft",
    "baichuan": "baichuan",
    "bytedance": "bytedance",
    "alibaba": "qwen",
    "ling": "ling",
    "inception": "inception",
    "ai21": "ai21",
}


def _extract_provider(model_id: str) -> str:
    """从 model_id 提取 provider，如 'deepseek/deepseek-chat' → 'deepseek'"""
    prefix = model_id.split("/")[0].lower()
    for key, value in PROVIDER_MAP.items():
        if key in prefix:
            return value
    return prefix


async def fetch_openrouter(
    client: Optional[httpx.AsyncClient] = None,
) -> list[ModelPrice]:
    """从 OpenRouter API 获取所有模型的定价数据。

    Returns:
        归一化的 ModelPrice 列表
    """
    close_client = False
    if client is None:
        client = httpx.AsyncClient(timeout=30.0, follow_redirects=True)
        close_client = True

    try:
        resp = await client.get(OPENROUTER_API)
        resp.raise_for_status()
        data = resp.json()
    finally:
        if close_client:
            await client.aclose()

    models: list[ModelPrice] = []
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    for item in data.get("data", []):
        model_id = item.get("id", "")
        if not model_id:
            continue

        name = item.get("name", model_id)
        pricing = item.get("pricing", {})
        prompt_price = float(pricing.get("prompt", "0") or "0")
        completion_price = float(pricing.get("completion", "0") or "0")

        # 转换为每百万 token 定价
        input_usd = round(prompt_price * 1_000_000, 4)
        output_usd = round(completion_price * 1_000_000, 4)

        provider = _extract_provider(model_id)
        provider_label = PROVIDER_LABELS.get(provider, provider)

        is_free = (input_usd == 0 and output_usd == 0)

        models.append(ModelPrice(
            model_id=model_id,
            display_name=name,
            provider=provider,
            provider_label=provider_label,
            input_price_usd=input_usd,
            output_price_usd=output_usd,
            context_window=item.get("context_length", 0),
            max_output_tokens=item.get("top_provider", {}).get("max_completion_tokens", 0),
            is_free=is_free,
            category=categorize(model_id),
            source="openrouter",
            source_url=f"https://openrouter.ai/{model_id}",
            updated_at=now,
        ))

    return models
