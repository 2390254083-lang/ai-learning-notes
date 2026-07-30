# 03 — Token 计算 & 成本估算

> 第 1 周 · Prompt Engineering
> 用时：30 分钟

---

## 一、Token 是什么

Token 是大模型处理文本的最小单位，不等于单词也不等于汉字。

| 语言 | 换算 | 例子 |
|------|------|------|
| 英文 | 1 token ≈ 0.75 个单词 | "I love AI" 3 个词 ≈ 4 token |
| 中文 | 1 汉字 ≈ 1-2 token | "我爱人工智能" 6 字 ≈ 10 token |

> 1000 token ≈ 750 英文单词 ≈ 500-600 汉字

---

## 二、插件的实际消耗

每次调用 = System Prompt + User Prompt + AI 返回

以翻译 500 字英文文章为例：
- System Prompt：约 100 token
- 用户选中文章：约 670 token
- AI 返回翻译：约 500 token
- **合计：约 1300 token/次**

---

## 三、主流模型价格

| 模型 | 输入 (每 1M token) | 输出 (每 1M token) |
|------|--------------------|--------------------|
| GPT-4o | $2.50 | $10.00 |
| GPT-4o-mini | $0.15 | $0.60 |
| Claude 3.5 Sonnet | $3.00 | $15.00 |
| DeepSeek V3 | ¥1.00 | ¥2.00 |

插件每次调用的费用：
- GPT-4o-mini：≈ 0.002 元/次，1 块钱能用 500 次
- Claude 3.5 Sonnet：≈ 0.05 元/次，1 块钱能用 20 次

---

## 四、省 Token 的方法

1. **System Prompt 精简** — 50 字和 500 字效果差异不大，成本差 10 倍
2. **长对话裁剪历史** — 只保留最近几轮
3. **简单任务用便宜模型** — 翻译总结用 mini/Haiku
4. **缓存 System Prompt** — Claude 和 OpenAI 都支持

---

## 五、实操

去 OpenAI Tokenizer（platform.openai.com/tokenizer）把插件三个 default prompt 粘贴进去，看实际 token 数。
