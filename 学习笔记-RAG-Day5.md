# Day 5: RAG 检索增强生成 — 原理 + 实战

> 第 2 周 · RAG
> 用时：2-3 小时（含原理 + 代码实战）

---

## 一、RAG 是什么？

RAG = Retrieval-Augmented Generation = 检索增强生成

**解决的问题：**
- LLM 会"幻觉"——不知道的瞎编
- LLM 有知识截止日期——不知道最新内容、不知道你的私有文档

**核心思路：** 提问之前，先从文档库里检索相关资料，塞给 LLM 一起看。相当于给 LLM"开卷考试"。

---

## 二、RAG 四步流程

```
加载文档 --> 文本分割 --> 向量化存储 --> 检索生成
```

### 步骤 1: 加载文档
用 PyPDF / LangChain Loader 读入 PDF、TXT 等格式。

### 步骤 2: 文本分割（Chunking）
长文档切成 500-1000 字的小块。相邻块有重叠（overlap），避免一句话被拦腰截断。

### 步骤 3: 向量化存储
用 Embedding 模型把每段文字转成向量（语义指纹），存进向量数据库。

**什么是向量？** 把文字映射到高维空间的一串数字。意思相近的文字，向量也相近。

```
"猫是动物"  -> [0.1, 0.8, -0.3, ...]
"狗是宠物"  -> [0.2, 0.7, -0.2, ...]  <- 数字接近！
"今天晴天"  -> [-0.6, -0.1, 0.9, ...] <- 数字差远了
```

### 步骤 4: 检索 + 生成
- 用户提问 -> 问题向量化 -> 去向量库找最相似的文档块
- 把文档块 + 原问题一起发给 LLM -> LLM 基于文档回答

---

## 三、本次实战技术栈

| 组件 | 技术 | 费用 |
|------|------|------|
| Embedding | sentence-transformers (all-MiniLM-L6-v2) | 免费，本地运行 |
| 向量数据库 | Chroma | 免费，本地存储 |
| 聊天模型 | DeepSeek (deepseek-chat) | 按量付费，很便宜 |
| 框架 | LangChain | 开源 |

---

## 四、踩坑记录

1. **LangChain 版本升级**：新版 LangChain 把 import 路径全改了
   - `langchain.chains` -> `langchain_classic.chains`
   - `langchain_community.vectorstores.Chroma` -> `langchain_chroma.Chroma`
   - 解决方案：安装 `langchain-classic` + `langchain-chroma`

2. **Windows GBK 编码**：代码里有 emoji 会报 UnicodeEncodeError
   - 解决方案：`export PYTHONIOENCODING=utf-8`，代码全用纯文本

3. **国内访问 HuggingFace 慢**：下载 Embedding 模型很慢
   - 解决方案：`export HF_ENDPOINT=https://hf-mirror.com`

4. **sentence-transformers 安装慢**：包很大（torch + transformers 几个 G）
   - 解决方案：用清华镜像 `pip install -i https://pypi.tuna.tsinghua.edu.cn/simple`

---

## 五、面试能说的

> "RAG 就是在给 LLM 发请求之前，先用用户问题去向量数据库检索相关文档，把文档内容和问题一起发给模型。核心流程：文档加载 -> 文本分割 -> 向量化存储 -> 检索增强生成。我用 LangChain + Chroma + DeepSeek 实现过一个文档问答系统，上传 PDF 后可以基于文档内容提问，AI 会引用原文回答。"

---

## 六、代码地址

`E:\学习计划\项目2：RAG文档问答\rag_app.py`

运行方式：
```bash
cd 项目2：RAG文档问答
source venv/Scripts/activate
python rag_app.py --file test_doc.txt
```
