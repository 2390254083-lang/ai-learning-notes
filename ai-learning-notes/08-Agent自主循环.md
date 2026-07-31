# Day 7：Agent — 把 Function Calling 串成一个循环

> 第 4 周 · Agent 原理
> 用时：2 小时（一个可工作的自主 Agent）

---

## 一、Function Calling 和 Agent 差在哪

昨天做的 Function Calling 是单轮工具调用：

用户提问 → AI 决定调哪个工具 → 执行拿到结果 → 还给 AI → 输出答案

Agent 把它改成了循环：

```
Think（想下一步）→ Act（调工具）→ Observe（看结果）
    → Think（继续还是停？）→ Act → Observe → ...
    → 够了 → 输出最终结果
```

**一句话：Function Calling 是一问一答，Agent 是多步自主执行。**

---

## 二、Agent 循环的实现

只改了两个地方：

### 1. 加一个"结束"工具
```python
finish_task(summary):
    """Agent 自己决定什么时候够——调这个工具表示完成"""
```

之前是人判断"信息够了"，现在是 Agent 自己判断。

### 2. 把单次调用包进循环
```python
for i in range(1, MAX_ITERATIONS + 1):
    response = client.chat.completions.create(messages=messages, tools=TOOLS)
    msg = response.choices[0].message

    if msg.tool_calls:
        # 执行工具，拿到结果，放回 messages，继续循环
        ...
        if 调了 finish_task:
            return  # 结束
    else:
        # AI 忘了调工具，提醒它
        ...
```

就这么简单。单次 Function Calling + 循环 + 一个"我好了"信号 = Agent。

### 3. 知识库扩展到 16 条
覆盖 Agent、RAG、LangChain、CrewAI、Token、Embedding、Prompt Engineering 等，让 Agent 有足够内容可以做多步搜索。

---

## 三、实际运行效果

研究目标：`帮我研究一下 RAG 和 Agent 的区别`

```
-- 第1步 --
  调用 search_knowledge
  返回: RAG（检索增强生成）核心流程：文档加载 → ...
-- 第2步 --
  调用 search_knowledge
  返回: AI Agent 是能自主决策、使用工具、完成多步任务...
-- 第3步 --
  调用 finish_task
  输出完整对比总结
完成 (3步)
```

Agent 主动搜了 2 次不同关键词，收集够信息后自己结束并输出总结。

---

## 四、关键技术点

| 问题 | 答案 |
|------|------|
| Agent 怎么知道什么时候停？ | 给它一个 `finish_task` 工具，它搜够了就自己调 |
| 怎么防止无限循环？ | 设 `MAX_ITERATIONS`，比如 10 步强制停止 |
| Agent 怎么知道搜什么？ | System Prompt 里写好规则——至少搜 2 次不同关键词 |
| 和 LangChain Agent 的区别？ | LangChain 把循环封装好了，只需定义工具和 prompt。原理一模一样。 |

---

## 五、面试能聊什么

1. **Agent 核心循环** — Think → Act → Observe → Think，每一步干什么
2. **Agent 和 Function Calling 的区别** — 单次 vs 多步循环
3. **怎么让 Agent 自己停** — finish_task 工具的巧妙之处
4. **MAX_ITERATIONS 防无限循环** — 生产环境必须有限制
5. **Agent = LLM + 工具 + 记忆 + 规划** — 四个组成部分

---

## 项目文件

`项目4：Agent自主循环/agent.py`
启动：`python agent.py`

下一步：用真实搜索 API 替换本地知识库，让 Agent 能搜互联网。
