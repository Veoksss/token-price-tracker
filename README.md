# 🪙 LLM Token 价格追踪

每日自动抓取 **340+ 大模型 API 定价**，生成价格对比表 + 套利机会分析 + 价格变动提醒。

> **Token 出海三步走 · 第一步**：用这个站积累 AI API 经济学的领域认知和流量，为后续 SaaS 和 API 代理打基础。

## 功能

- 📊 **全模型价格对比表** — 340+ 模型，按价格排序，支持按类别/搜索筛选
- 🇨🇳 **国产 vs 海外价差** — 实时展示国产模型（DeepSeek/Qwen/Kimi）vs 美国模型的成本差距
- 📈 **价格变动追踪** — 检测 24h 内的 API 调价，降价/涨价一目了然
- 💰 **套利发现** — 自动匹配同级别模型，标出套利空间

## 当前数据（实时更新）

| 指标 | 数值 |
|------|------|
| 国产模型均价 | ~$0.30 / 百万 token |
| 美国模型均价 | ~$4.81 / 百万 token |
| **平均价差** | **~16 倍** |
| 最实惠模型 | 低至 $0.01 / 百万 token |

## 一键部署

### 1. Fork 本仓库

### 2. 启用 GitHub Pages

**Settings → Pages → Source** → `Deploy from a branch` → 选 `gh-pages` → Save

### 3. 触发首次运行

**Actions → Token Price Tracker → Run workflow**

### 4. 访问

`https://<用户名>.github.io/token-price-tracker/`

之后每天北京时间 8:00 自动更新，**零费用、零维护**。

## 本地运行

```bash
pip install -r requirements.txt
python -m src.main
# 打开 output/index.html
```

## 数据来源

[OpenRouter API](https://openrouter.ai/api/v1/models) — 公开 JSON 接口，覆盖 340+ 模型定价。

## 与 ai-daily-digest 的关系

两个项目使用相同的架构（异步抓取 + 数据处理 + Jinja2 渲染 + GitHub Pages 部署），技术栈完全一致：

```
ai-daily-digest    → 抓 AI 新闻 → LLM 摘要 → 日报
token-price-tracker → 抓 API 价格 → 对比分析 → 比价表
```

## 在 Token 出海路线图中的位置

```
现在你在 ► 第一步：价格追踪站（本项目）
              ↓ 积累：领域认知 + SEO 流量 + 用户信任

第二步：AI SaaS 出海
  从价格表中找到"价差最大 + 质量够用"的模型组合
  → 基于廉价国产模型开发付费 AI 工具卖给海外客户
  → 示例：AI SEO 写作工具（底层 DeepSeek，成本 $0.0001/篇，售价 $19/月）

第三步：API 代理平台
  有了 SaaS 客户基础后，向上游整合
  → 聚合国产模型 API，提供 OpenAI 兼容接口
  → 客户从你用 SaaS → 直接用你的 API
```

## License

MIT
