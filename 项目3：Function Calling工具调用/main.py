"""
Function Calling 多工具 Demo
让 AI 自动选择工具：查天气、算数学、查时间、搜资料

用法:
  python main.py
  > 北京今天天气怎么样？
  > 帮我算 123 * 456
  > 现在几点了？
"""

import os
import json
import urllib.request
import urllib.parse
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from openai import OpenAI

# ---- 初始化 ----
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)

# ============================================================
# 第 1 步：定义工具
# ============================================================

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询指定城市今天的天气，返回温度、天气状况、湿度",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "城市名称，如 北京、上海、深圳",
                    }
                },
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "执行数学计算，支持加减乘除、幂运算、括号等",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "数学表达式，如 (123 + 456) * 2",
                    }
                },
                "required": ["expression"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "获取当前日期和时间",
            "parameters": {
                "type": "object",
                "properties": {
                    "timezone": {
                        "type": "string",
                        "description": "时区，如 北京时间、纽约时间，默认北京时间",
                    }
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_knowledge",
            "description": "搜索知识库，查询技术概念、名词解释等",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜索关键词",
                    }
                },
                "required": ["query"],
            },
        },
    },
]

# ============================================================
# 第 2 步：实现工具（真正干活的函数）
# ============================================================

def get_weather(city: str) -> str:
    """通过 wttr.in 免费 API 获取真实天气数据"""
    city_clean = city.replace("市", "").strip()
    url = f"https://wttr.in/{urllib.parse.quote(city_clean)}?format=j1"

    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read().decode())

        current = data["current_condition"][0]
        return (
            f"{city}当前天气：{current['weatherDesc'][0]['value']}，"
            f"温度 {current['temp_C']}°C（体感 {current['FeelsLikeC']}°C），"
            f"湿度 {current['humidity']}%，"
            f"风向 {current['winddir16Point']}，风速 {current['windspeedKmph']}km/h，"
            f"能见度 {current['visibility']}km"
        )
    except Exception as e:
        return f"查询{city}天气失败：{e}"


def calculate(expression: str) -> str:
    """安全计算数学表达式"""
    # 只允许数字、运算符、括号、空格
    allowed = set("0123456789+-*/().%^ eE")
    cleaned = "".join(c for c in expression if c in allowed)
    try:
        result = eval(cleaned)
        return f"计算结果：{expression} = {result}"
    except Exception as e:
        return f"计算出错：{e}"


def get_current_time(timezone: str = "") -> str:
    """获取当前时间"""
    now = datetime.now()
    return f"当前时间：{now.strftime('%Y年%m月%d日 %H:%M:%S')}（北京时间）"


def search_knowledge(query: str) -> str:
    """模拟知识库搜索"""
    kb = {
        "function calling": "Function Calling 是让大模型自动选择并调用外部函数/API 的能力。流程：①定义工具列表 → ②用户提问 → ③AI 返回 function_call → ④执行函数 → ⑤把结果还给 AI → ⑥AI 生成最终回答。OpenAI 叫 Function Calling，Anthropic 叫 Tool Use，本质相同。",
        "tool use": "Tool Use 是 Claude API 中的 Function Calling 机制。你定义 tool 的 name、description、input_schema，Claude 在需要时返回 tool_use 块，你的代码执行后将 tool_result 返回。支持并行调用多个工具。",
        "rag": "RAG（检索增强生成）的核心流程：文档加载 → 文本分割(chunk) → 向量化(embedding) → 存入向量数据库 → 用户提问时检索相关文本块 → 把文本块+问题一起发给 LLM → LLM 基于真实资料回答。解决了 LLM 幻觉和知识截止日期两个问题。",
        "agent": "AI Agent 是能自主决策、使用工具、完成多步任务的 AI 程序。核心循环：Think(思考) → Act(行动/调工具) → Observe(观察结果) → Think(再思考)。Agent = LLM + 工具 + 记忆 + 规划能力。",
    }
    for key, value in kb.items():
        if key in query.lower():
            return value
    return f"未找到「{query}」的相关知识。已知内容：Function Calling、Tool Use、RAG、Agent。"


# 工具名 → 函数映射
TOOL_MAP = {
    "get_weather": get_weather,
    "calculate": calculate,
    "get_current_time": get_current_time,
    "search_knowledge": search_knowledge,
}

# ============================================================
# 主循环
# ============================================================

def run():
    messages = [
        {"role": "system", "content": "你是一个有用的AI助手。用户提问时，如果需要查天气、算数学、查时间、搜资料，请使用对应工具获取真实数据后再回答。不要编造数据。"}
    ]

    print("=" * 60)
    print("[AI 工具助手] Function Calling Demo")
    print("   可以：查天气 | 算数学 | 查时间 | 搜知识")
    print("   输入 quit 退出")
    print("=" * 60)

    while True:
        try:
            user_input = input("\n你: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见!")
            break

        if not user_input:
            continue
        if user_input.lower() == "quit":
            print("再见!")
            break

        messages.append({"role": "user", "content": user_input})

        # ---- 第 3 步：调用 AI，AI 决定是否调工具 ----
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            tools=TOOLS,
        )

        msg = response.choices[0].message

        # ---- 情况 A：AI 要调工具 ----
        if msg.tool_calls:
            # 先把 AI 的 tool_calls 加入对话
            messages.append(msg)

            for tool_call in msg.tool_calls:
                name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)

                print(f"\n[AI 决定调用] → {name}({args})")

                # ---- 第 4 步：执行函数 ----
                func = TOOL_MAP.get(name)
                if func:
                    result = func(**args)
                else:
                    result = f"错误：未找到工具 {name}"

                print(f"[工具返回] → {result[:100]}")

                # 把 tool_result 加入对话
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result,
                })

            # ---- 第 5 步：把结果还给 AI，生成最终回答 ----
            response2 = client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
            )
            final_msg = response2.choices[0].message
            messages.append(final_msg)
            print(f"\nAI: {final_msg.content}")

        # ---- 情况 B：AI 直接回答（不需要工具） ----
        else:
            messages.append(msg)
            print(f"\nAI: {msg.content}")


if __name__ == "__main__":
    run()
