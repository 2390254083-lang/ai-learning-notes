# Day 6：Function Calling — 让 AI 学会调用工具

> 第 3 周 · Function Calling / Tool Use
> 用时：2 小时（RAG Web UI 补充 + Function Calling 原理 + 项目实战）

---

## 一、今天做了什么

### 1. 给 RAG 项目加了 Web UI

用 Streamlit 把命令行版的 RAG 文档问答改成了浏览器里的聊天界面：
- 侧边栏上传 PDF/TXT → 点击处理 → 主区域聊天问答
- 用了 `@st.cache_resource` 缓存模型，只加载一次
- 踩坑：HuggingFace 国内下载慢 → 加了 `HF_ENDPOINT=https://hf-mirror.com` 镜像

### 2. 做了一个多工具 Function Calling Demo

可以：查天气 | 算数学 | 查时间 | 搜知识

**核心代码结构：**
```python
TOOLS = [{name, description, parameters}, ...]  # ① 定义工具
TOOL_MAP = {"name": func}                        # ② 工具名→函数映射
response = client.chat.completions.create(...)     # ③ AI 决定调哪个工具
if msg.tool_calls: func(**args)                    # ④ 执行函数
response2 = client.chat.completions.create(...)    # ⑤ 结果还给 AI
```

**升级：天气从 mock 数据换成了真实 API**

接入 `wttr.in` 免费天气 API，每次查询返回实时数据。关键点——只改工具函数实现，AI 调用逻辑完全不用动。这就是 Function Calling 解耦的威力。

---

## 二、Function Calling 核心原理

### 解决什么问题
LLM 只能"说"，不能"做"。Function Calling 让它能调用外部工具——查天气、算数学、搜资料。

### 5 步流程

```
① 定义工具列表（每个工具的 name + description + 参数格式）
    ↓
② 用户提问，AI 决定要不要调工具、调哪个、传什么参
    ↓
③ AI 返回 function_call，不是最终回答
    ↓
④ 你的代码执行对应函数，拿到真实数据
    ↓
⑤ 把结果还给 AI，AI 基于真实数据生成最终回答
```

**核心认知：AI 不动手。它只告诉你"我想调 X 函数、传 Y 参数"，谁来执行？你。执行完的结果还给 AI，AI 再润色成人话。**

### 关键设计决策

| 问题 | 答案 |
|------|------|
| AI 怎么知道调哪个工具？ | 靠 `name` + `description`，描述越清晰越准 |
| 多个工具怎么选？ | AI 根据语义自动判断，不用写 if-else |
| 调错怎么办？ | 工具返回错误信息，AI 看到后会自己修正 |
| OpenAI vs Claude 的区别？ | 本质相同，OpenAI 叫 Function Calling，Claude 叫 Tool Use，返回格式略有差异 |
| 和普通 API 调用的区别？ | 普通方法要写死 `if 天气 then 调天气API`；Function Calling 让 AI 自己判断意图 |

### 多工具协作示例

```
用户："帮我查北京天气，然后算一下 25*3"
  → AI 先调 get_weather("北京")
  → 拿到结果后，再调 calculate("25*3")
  → 两次结果整合后一次性回答
```

这就是多步工具调用，是 Agent 自主行为的基础。

---

## 三、踩坑记录

1. **Streamlit 的 `@st.cache_resource`**：Embedding 模型 80MB，每次刷新都重载太慢，用 cache_resource 只加载一次
2. **HuggingFace 镜像**：国内下载模型设置 `HF_ENDPOINT=https://hf-mirror.com`，否则超时
3. **Streamlit session_state**：vectorstore 必须存在 `st.session_state` 里，否则每次交互都会丢失
4. **DeepSeek 的 Tool Calling**：兼容 OpenAI 格式，直接用 `openai` 包 + `base_url` 指向 DeepSeek 即可，写法不变

---

## 四、项目文件

- **项目 2 RAG Web UI**：`项目2：RAG文档问答/app.py`
  - 启动：`streamlit run app.py`
- **项目 3 Function Calling**：`项目3：Function Calling工具调用/main.py`
  - 启动：`python main.py`
  - 4 个工具：天气、计算、时间、知识搜索
  - 技术栈：DeepSeek API（OpenAI 兼容格式）
