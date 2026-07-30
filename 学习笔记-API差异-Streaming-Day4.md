# Day 4：API 差异 & 流式输出（Streaming）

> 第 1 周 · Prompt Engineering + API 精通
> 用时：1-2 小时（含代码实战）

---

## 一、OpenAI API vs Claude API 核心差异

### 1. 请求体：System Prompt 放哪

```
OpenAI:                            Claude:
{                                  {
  "messages": [                      "system": "你是翻译助手",
    {"role": "system",              "messages": [
      "content": "你是翻译助手"},      {"role": "user",
    {"role": "user",                    "content": "翻译这段"}
      "content": "翻译这段"}         ],
  ],                               "max_tokens": 1024
}                                  }
```

OpenAI 把 system prompt 放在 messages 数组里（role=system），Claude 用独立的 `system` 字段。

### 2. 响应体：结果藏在哪里

```
OpenAI:                            Claude:
choices[0]                         content[0]
  .message                           .text
    .content
```

**面试一句话：** "OpenAI 的 system prompt 在 messages 数组里，Claude 用独立 system 字段；响应体 OpenAI 是 choices[0].message.content，Claude 是 content[0].text。"

### 3. 其他差异

| | OpenAI | Claude |
|---|---|---|
| API 版本头 | 不需要 | `anthropic-version` 必须 |
| stream 参数 | `stream: true` | `stream: true` |
| SSE 事件格式 | `choices[0].delta.content` | `content_block_delta` → `delta.text` |

---

## 二、流式输出（SSE）

### 原理

正常 API：发送请求 → 等服务端生成完毕 → 一次性返回全部结果（等 3-10 秒）

流式：发送请求 → 服务端生成一个字就发一个字 → 页面逐字显示（打字机效果）

底层是 **SSE（Server-Sent Events）**：HTTP 连接不断开，服务端持续推送 `data:` 行。

### 三个服务商的 SSE 差异

解析 SSE 时提取文本的字段：

| 服务商 | 提取路径 |
|--------|---------|
| OpenAI | `json.choices[0].delta.content` |
| Claude | `json.type === 'content_block_delta'` → `json.delta.text` |
| DeepSeek | 同 OpenAI |

### 通用 SSE 解析器

```js
async function readSSEStream(response, extractText, onChunk) {
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let fullText = '', buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop() || '';

    for (const line of lines) {
      if (!line.trim() || !line.startsWith('data: ')) continue;
      const data = line.trim().slice(6);
      if (data === '[DONE]') continue;
      try {
        const text = extractText(JSON.parse(data));
        if (text) { fullText += text; onChunk(text); }
      } catch (e) {}
    }
  }
  return fullText.trim();
}
```

三个服务商共用同一个读取器，只是 `extractText` 回调不同。

---

## 三、Week 1 收尾

至此 Week 1（Prompt Engineering + API 精通）全部学完：

- Day 1: System Prompt 设计三条原则（角色、约束、示例）
- Day 2: Few-shot + CoT + 结构化输出
- Day 3: Token 计算 & 成本估算
- Day 4: API 差异 & 流式输出（含代码实战）

**产出：**
- 插件用了 Day 2 的技巧优化了 prompt
- 插件加了 Streaming，体验从"干等"变成"打字机"
- 面试问到 Prompt Engineering 和 API 调用，能聊四天内容
