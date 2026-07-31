"""
AI Agent — 自主多步执行
核心：Think → Act → Observe → Think → ... 循环
用户给目标，Agent 自己拆任务、调工具、判断是否完成

用法:
  python agent.py
  > 帮我研究一下 Function Calling 和 Agent 的区别
"""

import os
import json
import urllib.request
import urllib.parse
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from openai import OpenAI

_client = None

def get_client():
    global _client
    if _client is None:
        _client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com",
        )
    return _client

# ============================================================
# 工具定义
# ============================================================

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_knowledge",
            "description": "搜索 AI 知识库，返回相关概念的解释。可以多次调用，每次用不同关键词。",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜索关键词，如 'Function Calling'、'RAG'、'Agent'",
                    }
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "finish_task",
            "description": "当你收集到足够信息、可以输出最终结果时调用。调用后任务结束。",
            "parameters": {
                "type": "object",
                "properties": {
                    "summary": {
                        "type": "string",
                        "description": "最终的研究总结，要完整、结构化",
                    }
                },
                "required": ["summary"],
            },
        },
    },
]

# ============================================================
# 知识库
# ============================================================

KNOWLEDGE_BASE = {
    "function calling": "Function Calling 是让大模型调用外部工具的能力。流程：定义工具列表 → 用户提问 → AI 返回 function_call（JSON） → 开发者执行函数 → 结果还给 AI → AI 生成最终回答。OpenAI 叫 Function Calling，Anthropic 叫 Tool Use。本质相同，都是让 AI 输出一个结构化的'调用指令'而不是直接回答。",
    "tool use": "Tool Use 是 Anthropic Claude API 的 Function Calling 实现。定义 tool 的 name、description、input_schema，Claude 在需要时返回 tool_use 内容块。特色：支持并行工具调用（一次返回多个 tool_use），流式 tool_use（边生成边返回）。https://docs.anthropic.com/en/docs/build-with-claude/tool-use",
    "agent": "AI Agent 是能自主决策、使用工具、完成多步任务的 AI 程序。核心循环：Think（推理下一步做什么）→ Act（调用工具）→ Observe（观察结果）→ Think（继续还是结束）。Agent = LLM + 工具 + 记忆 + 规划能力。和 Function Calling 的关键区别：Function Calling 是一问一答，Agent 是多步自主循环。",
    "agent 循环": "Agent 循环（Agentic Loop）是 Agent 的核心运转机制。每一步：① Think：AI 分析当前状态，决定下一步行动 ② Act：调用对应工具 ③ Observe：获取工具返回结果 ④ 判断：目标达成了吗？没达成继续 ①。关键是让 AI 自己判断何时结束，而不是外部硬编码停止条件。",
    "react": "ReAct（Reasoning + Acting）是 Agent 最经典的运行模式。AI 交替进行推理和行动：先'思考'（分析现状、规划下一步），再'行动'（调用工具），观察到结果后再'思考'。论文：Yao et al., 2022。LangChain 的 Agent 框架底层就是 ReAct 模式。",
    "rag": "RAG（检索增强生成）核心流程：文档加载 → 文本分割（chunk） → 向量化（Embedding） → 存入向量数据库 → 用户提问时检索最相关文本块 → 文本块+问题一起发给 LLM → LLM 基于真实资料回答。解决了 LLM 的两个硬伤：幻觉（编造事实）和知识截止日期。",
    "embedding": "Embedding（嵌入）是把文字转成向量的技术。一句话 → 384 维或 1536 维的数字数组。语义相近的文字，向量空间中的距离也近。比如'猫'和'猫咪'的向量很近，'猫'和'汽车'的向量很远。常用模型：OpenAI text-embedding-3-small（付费），sentence-transformers all-MiniLM-L6-v2（免费本地）。",
    "langchain": "LangChain 是 AI 应用开发框架，核心概念：① Chain（链式调用，把多个步骤串起来）② Agent（自主决策，动态选择工具）③ Tool（工具封装，统一接口）④ Memory（记忆管理，让 Agent 记得之前的对话）。优势：组件化、社区大、文档多。劣势：抽象层太多，简单事情绕弯路。",
    "crewai": "CrewAI 是 Multi-Agent 框架，让你创建多个 AI Agent 协作完成任务。核心概念：Agent（角色+目标+工具）、Task（具体任务）、Crew（Agent 团队）。比如：研究员 Agent 搜资料、分析师 Agent 整理、作者 Agent 写报告。适合复杂多步骤项目，但比单 Agent 更难调试和控制。",
    "langchain vs crewai": "LangChain 和 CrewAI 不是直接竞品。LangChain 是通用 LLM 框架（Chain + Agent + Tool + Memory），CrewAI 专注于 Multi-Agent 协作场景。简单任务用 LangChain 就够了，多角色协作场景考虑 CrewAI。如果只是一个 Agent 调几个工具，LangChain 足够；如果需要多个 Agent 分工协作，用 CrewAI。",
    "deepseek": "DeepSeek（深度求索）是中国 AI 公司，开源了 DeepSeek-V3、DeepSeek-R1 等模型。API 价格极低（deepseek-chat 输入 ¥1/百万 token，输出 ¥2/百万 token），兼容 OpenAI 接口格式。对学习项目和初期产品是很好的选择。",
    "token": "Token 是 LLM 处理文本的最小单位。英文约 1 单词 = 1.3 token，中文约 1 个字 = 2 token。Token 是计费单位。模型有上下文长度限制（如 128K token），超出会截断。计算 token 用 tiktoken 库。输入和输出都按 token 收费，输出通常更贵。",
    "prompt engineering": "Prompt Engineering 是设计提示词以让 LLM 输出更好结果的技术。核心技巧：① System Prompt 设定角色和约束 ② Few-shot 给示例 ③ Chain-of-Thought 让 AI 在推理时'念出思考过程' ④ 结构化输出要求（JSON/Markdown 格式）。原则：清晰 > 模糊，具体 > 笼统，有例子 > 没例子。",
    "system prompt": "System Prompt（系统提示词）是给 AI 设定基础行为规则的提示词。通常放在对话最开始，优先级最高。内容包括：角色定义（'你是一个...'）、行为约束（'不要...'）、输出格式（'以 JSON 返回...'）。System Prompt 是单向的——用户看不到，但 AI 全程遵守。",
    "vector database": "向量数据库专门存储和检索向量（高维数字数组）。和传统数据库的区别：传统数据库查'精确匹配'，向量数据库查'语义相似'。常用：Chroma（轻量本地）、Pinecone（云服务）、Weaviate、Qdrant。RAG 系统中用来存储文档的向量，用户提问时检索最相关的文本块。",
    "streaming": "流式输出（Streaming）是 LLM 一个字一个字返回结果的方式。用户体验更好（不用等完整回答），但解析麻烦（token 可能被拆开）。实现方式：设置 stream=True，然后逐块读取。OpenAI 和 Claude API 都支持。项目 1 的浏览器翻译插件已经加过了。",
}

# ============================================================
# 工具实现
# ============================================================

def search_knowledge(query: str) -> str:
    """搜索本地知识库"""
    q = query.lower().strip()
    results = []
    for key, value in KNOWLEDGE_BASE.items():
        if q in key or key in q:
            results.append(f"【{key}】{value}")
    if not results:
        # 模糊匹配：检查每个词
        for word in q.split():
            for key, value in KNOWLEDGE_BASE.items():
                if word in key and f"【{key}】{value}" not in results:
                    results.append(f"【{key}】{value}")
    if not results:
        return f"未找到关于「{query}」的知识。请换一个关键词试试。"
    return "\n\n".join(results[:3])


def finish_task(summary: str) -> str:
    """Agent 调用此工具表示任务完成"""
    return f"[TASK_COMPLETE]\n{summary}"


TOOL_MAP = {
    "search_knowledge": search_knowledge,
    "finish_task": finish_task,
}

# ============================================================
# Agent 核心循环
# ============================================================

MAX_ITERATIONS = 10  # 防止无限循环

SYSTEM_PROMPT = """你是一个 AI 研究助手 Agent。你有以下能力：
- 用 search_knowledge 搜索 AI 知识库（可以多次调用，每次不同关键词）
- 用 finish_task 输出最终结果

工作方式：
1. 收到用户的目标后，先 Think：需要了解什么？从哪里开始搜？
2. 调用 search_knowledge 收集信息
3. 观察结果，判断信息够不够。不够就换关键词继续搜
4. 搜完后用 finish_task 输出结构化总结

重要规则：
- 至少要搜索 2 次（不同关键词），不要搜一次就结束
- 搜索完所有相关内容后，用 finish_task 输出完整的对比/总结
- 最后总结要包含：核心概念解释、关键区别、实际应用场景"""


def run_agent(user_goal: str):
    """执行 Agent 循环"""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_goal},
    ]

    print(f"目标: {user_goal}")

    for i in range(1, MAX_ITERATIONS + 1):
        print(f"\n-- 第{i}步 --")

        response = get_client().chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            tools=TOOLS,
        )

        msg = response.choices[0].message

        # ---- 情况 A：AI 要调工具 ----
        if msg.tool_calls:
            messages.append(msg)

            for tool_call in msg.tool_calls:
                name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)

                print(f"  调用 {name}")

                func = TOOL_MAP.get(name)
                result = func(**args) if func else f"错误：未找到工具 {name}"

                if name == "finish_task":
                    print(f"\n{result.split('[TASK_COMPLETE]', 1)[-1].strip()}")
                else:
                    short = result[:100].replace("\n", " ")
                    print(f"  返回: {short}...")

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result,
                })

                # 检查是否调了 finish_task
                if name == "finish_task":
                    print(f"\n完成 ({i}步)")
                    return

        # ---- 情况 B：AI 没调工具（可能想直接回答） ----
        else:
            # 如果 AI 没调工具也没调 finish_task，提醒它
            print(f"  AI 没调工具，提醒它...")
            messages.append({"role": "user", "content": "请使用 search_knowledge 搜索相关信息，收集完整后再用 finish_task 输出总结。不要直接回答。"})

    print(f"\n达到最大步数 {MAX_ITERATIONS}，强制结束")


def main():
    print("AI Agent 自主研究助手")
    print("给它一个话题，自己搜资料、整理、输出报告")
    print()

    while True:
        try:
            goal = input("研究目标 (quit 退出): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见!")
            break

        if not goal:
            continue
        if goal.lower() == "quit":
            print("再见!")
            break

        run_agent(goal)


if __name__ == "__main__":
    main()
