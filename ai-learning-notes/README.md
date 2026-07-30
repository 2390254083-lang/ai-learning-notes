# AI 应用开发 — 学习笔记

> 从零开始学 AI 应用层全栈开发，2 个月冲刺实习面试。

## 关于我

职场新人，大专学历，自学 AI 应用开发。目标岗位：AI 应用开发实习生。

学习方式：项目驱动，输出倒逼输入。允许做得烂，烂也比没做强。

## Week 1：Prompt Engineering + API 精通 ✅

| 序号 | 笔记 | 内容 |
|------|------|------|
| 01 | [System Prompt 设计](01-System-Prompt设计.md) | 角色、约束、示例三条核心原则 |
| 02 | [Few-shot + 思维链](02-Few-shot与思维链.md) | CoT、结构化输出、Few-shot 策略 |
| 03 | [Token 与成本](03-Token计算与成本.md) | 计费原理、各模型价格、省钱技巧 |
| 04 | [API 差异 + 流式](04-API差异与流式输出.md) | OpenAI vs Claude + SSE 流式输出 |
| 05 | [实战优化](05-Prompt三件套实战.md) | 插件 prompt 打磨，含测试对比 |

### 练习记录

- [插件 Prompt 对比](练习-插件对比.md)
- [提示词优化全记录](练习-提示词优化记录.md)

## Week 2：RAG（检索增强生成）🚧

| 序号 | 笔记 | 内容 |
|------|------|------|
| 06 | [RAG 实战——文档问答系统](06-RAG实战-文档问答.md) | 原理、四步流水线、代码讲解、面试要点 |

### 练习记录

- [RAG 代码](练习-RAG文档问答.py) — Python RAG 系统，支持 PDF/TXT，本地 Embedding + DeepSeek

## Week 3：Function Calling / Tool Use 🚧

| 序号 | 笔记 | 内容 |
|------|------|------|
| 07 | [Function Calling 实战](07-Function-Calling实战.md) | 原理、5 步流程、多工具 Demo、RAG Web UI |

### 练习记录

- [Function Calling Demo](../项目3：Function Calling工具调用/main.py) — 4 工具 AI 助手（天气/计算/时间/知识搜索），DeepSeek API

## 项目

- **[浏览器 AI 翻译插件](https://github.com/2390254083-lang/browser-translator)** — Chrome 扩展，选中文字 → AI 总结/翻译/解释。支持 OpenAI / Claude / DeepSeek，含流式输出。
- **[RAG 文档问答系统](https://github.com/2390254083-lang/rag-doc-qa)** — 上传 PDF/TXT，AI 基于文档内容回答。CLI + Web UI 双界面，本地 Embedding + DeepSeek。
- **[Function Calling 多工具 Demo](https://github.com/2390254083-lang/function-calling-demo)** — AI 自动选择天气/计算/时间/知识搜索工具，命令行交互。

## 链接

- GitHub: [@2390254083-lang](https://github.com/2390254083-lang)
