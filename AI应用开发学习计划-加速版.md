# AI 应用开发 — 两个月冲刺计划（实习面试向）

> 目标：2 个月内达到 AI 应用开发实习生的面试要求——能聊、能写、有作品
> 原则：只学面试会考的，只做能放进简历的

---

## 总览

| 周次 | 模块 | 产出 |
|------|------|------|
| 第 1 周 | Prompt Engineering + API 精通 | 优化后的插件 + 对比笔记 |
| 第 2 周 | RAG（检索增强生成） | 一个文档问答系统 |
| 第 3 周 | Function Calling / Tool Use | 一个 AI 命令行工具 |
| 第 4 周 | Agent 原理 + 框架 | 一个自主 Agent |
| 第 5-6 周 | 主项目：个人 AI 助手 Agent | 简历核心项目 |
| 第 7 周 | 补漏 + 项目打磨 + README | GitHub 完善 |
| 第 8 周 | 面试模拟 + 八股文 | 能过面试 |

---

## 第 1 周：Prompt Engineering + API 精通

**目标：** 能聊透 API 调用，能写出好 prompt，面试问到细节不虚

**内容：**
- System Prompt 设计（角色、约束、示例）
- Few-shot / Chain-of-Thought / 结构化输出
- Token 计算、成本估算
- OpenAI API vs Claude API 的差异（你已经踩过坑了）
- 流式输出（streaming）——给你的插件加上

**产出：**
- 插件 prompt 三件套优化
- 一篇笔记："三个 prompt 技巧让 AI 输出质量翻倍"

---

## 第 2 周：RAG（检索增强生成）

**目标：** 理解 RAG 全链路，能搭一个最小可用系统

**内容：**
- 为什么需要 RAG（LLM 的幻觉 + 知识截止问题）
- 嵌入（Embedding）是什么
- 向量数据库（Chroma / 本地 JSON 代替也行）
- 检索 → 增强 → 生成 的完整流程
- LangChain 最简用法（只学需要的部分）

**产出：**
- 一个命令行工具：上传 PDF → 提问 → AI 回答
- 技术栈：Python + Chroma + OpenAI API

---

## 第 3 周：Function Calling / Tool Use

**目标：** 让 AI 能调用外部工具——这是 Agent 的基础

**内容：**
- Function Calling 原理：让 AI 决定什么时候调什么函数
- OpenAI Function Calling / Claude Tool Use
- 多工具编排：多个工具时 AI 如何选择
- 错误处理：AI 调了不存在的函数怎么办

**产出：**
- 一个命令行工具："帮我查一下今天北京的天气" → AI 自动调天气 API
- 扩展到查快递、查汇率、查航班中的 2 个

---

## 第 4 周：Agent 原理

**目标：** 理解 Agent 循环，能用 LangChain 搭一个最简 Agent

**内容：**
- Agent 的核心循环：Think → Act → Observe → Think → ...
- 记忆管理（短期 vs 长期）
- ReAct 模式（Reasoning + Acting）
- LangChain Agent 最简用法

**产出：**
- 一个能"搜索 + 总结"的 Agent：给它一个话题，它自己搜、自己整理、输出报告

---

## 第 5-6 周：主项目 — 个人 AI 助手 Agent

**目标：** 这是你简历上最核心的项目，面试主要聊这个

**功能：**
> 用户说一句自然语言，Agent 自动拆解任务、调用工具、输出结果

比如：
- "帮我研究一下最近 AI 编程工具的趋势，整理成报告"
- Agent 自动：拆任务 → 搜索 → 读网页 → 整理 → 输出

**技术栈：**
- LangChain / CrewAI 二选一
- OpenAI / Claude API
- 搜索工具（SerpAPI 或 DuckDuckGo）
- 可选：网页抓取（BeautifulSoup）

**要求：**
- GitHub README 写清楚：做了什么、怎么运行、技术架构图
- 录一个 2 分钟 demo 视频

---

## 第 7 周：打磨

- 把前面所有项目的 README 写清楚
- GitHub 主页整理（pin 项目、写 profile README）
- 把你觉得最好的一个项目写一篇技术复盘文章

---

## 第 8 周：面试准备

**技术面常见问题：**
- Prompt Engineering 的核心原则是什么？
- RAG 的流程是怎样的？向量数据库干什么用的？
- Function Calling 和普通 API 调用有什么区别？
- Agent 的 Think-Act-Observe 循环怎么运作？
- Token 是什么？怎么算成本？
- OpenAI API 和 Claude API 的主要差异？

**行为面：**
- 为什么大专学历来投 AI 开发？
  - 你的版本：我自学了 2 个月，做了 3 个项目，代码都在 GitHub 上，你可以看。

**模拟面试：** 我可以在最后一周 mock 你一轮。

---

## 每天节奏

- 工作日：1-2 小时（晚上）
- 周末：4-6 小时（集中输出项目）
- 每周日发一篇笔记/周报

---

## 不改的原则（从原计划继承）

1. 项目驱动，不做完不发
2. 代码全部公开 GitHub
3. 允许做得烂，烂也比没做强
4. 每周输出一篇公开笔记
