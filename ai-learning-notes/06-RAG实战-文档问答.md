# Day 5：RAG 从原理到代码——我做了一个文档问答系统

> 第 2 周 · RAG 检索增强生成
> 用时：2 小时（含代码实战）

---

## 一、RAG 解决什么问题

LLM 有两个硬伤：
1. **知识截止日期**——训练数据停在某个时间点，之后的事不知道
2. **幻觉**——不知道的东西会瞎编，而且编得一本正经

RAG 的思路很朴素：**别让 AI 凭空回答，先给它找资料，让它照着资料说。**

---

## 二、RAG 的四步流水线

```
上传 PDF/TXT
    ↓
① 文档加载 → ② 文本分割 → ③ 向量化存储 → ④ 检索 + 生成回答
```

### ① 文档加载

```python
if ext == ".pdf":
    loader = PyPDFLoader(file_path)
elif ext == ".txt":
    loader = TextLoader(file_path, encoding="utf-8")
documents = loader.load()
```

LangChain 帮我们处理了不同格式的读取。PDF 按页加载，TXT 整体读入。

### ② 文本分割（最关键的一步）

```python
splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,      # 每块最多 800 字符
    chunk_overlap=100,   # 块与块之间有 100 字符重叠
)
chunks = splitter.split_documents(documents)
```

**为什么不能把整篇文档直接向量化？**
因为 Embedding 模型有最大输入长度（通常是 512 token），而且整篇文档的向量太"笼统"，搜不准具体内容。

**为什么要有 overlap？**
假设一句话是"今天的股价是 100 元"，如果刚好在 800 字符处切开，上半句在块 3，下半句在块 4，检索时就会丢失这段信息。overlap 让相邻块有 100 字符的重合地带。

### ③ 向量化存储

```python
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"},
)

vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="./chroma_db",
)
```

把我的学习笔记 `test_doc.txt` 转成了几百个 384 维的向量，存到本地 Chroma 数据库。

**我选本地 Embedding 模型的原因：**
- OpenAI 的 `text-embedding-3-small` 要花钱（虽然很便宜，$0.02/百万 token）
- 本地模型完全免费，而且跑 CPU 也够快
- 对于学习项目，80MB 的模型足够好用

**向量是什么？** 就是把文字变成一串数字，语义相近的文字数字也相近。比如"猫"和"猫咪"的向量距离很近，"猫"和"汽车"的向量距离很远。

### ④ 检索 + 生成

```python
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=vectorstore.as_retriever(search_kwargs={"k": 4}),
    return_source_documents=True,
)
```

用户提问时：
1. 问题也转成向量
2. 在向量库里找最相似的 4 个文本块（k=4）
3. 把这 4 个文本块 + 用户问题一起发给 DeepSeek
4. DeepSeek 基于真实资料回答，并附上来源

---

## 三、技术选型的考量

| 组件 | 我选的 | 为什么 |
|------|--------|--------|
| 聊天模型 | DeepSeek（deepseek-chat） | 价格极低，效果够用 |
| Embedding | HuggingFace 本地模型 | 免费，不依赖网络 |
| 向量库 | Chroma | 轻量，本地运行，无需注册 |
| 框架 | LangChain | 各组件拼装方便，社区最大 |

**一个实用的坑：** DeepSeek 接口兼容 OpenAI 格式，所以 LangChain 的 `ChatOpenAI` 类可以直接用，只需把 `base_url` 指向 `https://api.deepseek.com`。这叫"借壳上市"。

---

## 四、实际测试

用我的学习笔记 `test_doc.txt` 做测试——

**问：什么是 Token？**
> Token 是 LLM 处理文本的最小单位。英文约 1 个单词 = 1.3 个 Token，中文约 1 个字 = 2 个 Token。Token 是计费单位，输入和输出都按 Token 数收费。以 GPT-4o-mini 为例，输入 $0.15/1M tokens，输出 $0.60/1M tokens。

**问：RAG 的流程是什么？**
> RAG 的完整流程：1. 文档加载：读入 PDF、TXT 等各种格式的文档；2. 文本分割：将长文档切成 500-1000 字的文本块；3. 向量化存储：用 Embedding 模型将文本块转成向量，存入向量数据库；4. 检索增强生成：用户提问时，先将问题向量化，检索最相关的文档块，连同问题一起发给 LLM。

回答准确，没有幻觉，而且附带了来源。

---

## 五、这段代码面试能聊什么

1. **RAG 四个环节**（加载→分割→向量化→检索生成），每个环节为什么这么设计
2. **chunk_size 和 overlap** 怎么选，overlap 为什么重要
3. **Embedding 模型的选择**——花钱用 API 还是用本地免费模型，各自优劣
4. **为什么向量数据库能搜到"语义相近"的内容**——向量空间中距离近
5. **DeepSeek 借壳 OpenAI 接口**——知道 LangChain 的 ChatOpenAI 类怎么配 base_url

---

## 下一步

- 给这个 RAG 系统加个 Web UI（Gradio 或 Streamlit，十几行代码）
- 支持上传多个文档，建一个"个人知识库"
- 开始学 Function Calling——让 AI 能调外部 API
