"""
RAG 文档问答系统 -- DeepSeek 版
Embedding: 本地免费模型（sentence-transformers，无需 API Key）
聊天模型: DeepSeek

用法:
  python rag_app.py                     # 交互式选择文件
  python rag_app.py --file test.txt     # 直接指定文件
"""

import argparse
import os
import sys

from dotenv import load_dotenv
load_dotenv()

# -- 检查 API Key --
DEEPSEEK_KEY = os.getenv("DEEPSEEK_API_KEY")
if not DEEPSEEK_KEY:
    print("[ERROR] 请在 .env 文件中设置 DEEPSEEK_API_KEY")
    print("   格式: DEEPSEEK_API_KEY=sk-xxx")
    sys.exit(1)

# -- 导入 --
from langchain_openai import ChatOpenAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_classic.chains import RetrievalQA

# -- 配置 --
PERSIST_DIR = "./chroma_db"

# Embedding: 本地 HuggingFace 模型（首次运行会自动下载，约 80MB）
print("[INFO] 加载本地 Embedding 模型...")
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"},
)

# 聊天模型: DeepSeek（兼容 OpenAI 接口格式）
llm = ChatOpenAI(
    model="deepseek-chat",
    api_key=DEEPSEEK_KEY,
    base_url="https://api.deepseek.com",
    temperature=0.3,
)


# ============================================================
def load_and_split(file_path: str):
    """加载 PDF/TXT 并切成文本块"""
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        loader = PyPDFLoader(file_path)
    elif ext == ".txt":
        loader = TextLoader(file_path, encoding="utf-8")
    else:
        print(f"[WARN] 暂不支持 {ext} 格式，请用 PDF 或 TXT")
        sys.exit(1)

    documents = loader.load()
    print(f"[OK] 文档加载完成: {len(documents)} 页")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100,
        separators=["\n\n", "\n", ".", ".", " ", ""],
    )
    chunks = splitter.split_documents(documents)
    print(f"[OK] 分割完成: {len(chunks)} 个文本块")
    return chunks


def build_vectorstore(chunks):
    """向量化并存入 Chroma"""
    print("[INFO] 正在向量化...")

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=PERSIST_DIR,
    )
    print(f"[OK] 向量数据库已保存到 {PERSIST_DIR}/")
    return vectorstore


def chat_loop(vectorstore):
    """交互式问答"""
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=vectorstore.as_retriever(search_kwargs={"k": 4}),
        return_source_documents=True,
    )

    print("\n" + "=" * 60)
    print(">> 开始问答（输入 quit 退出）")
    print("=" * 60)

    while True:
        try:
            question = input("\n你的问题: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见!")
            break

        if not question:
            continue
        if question.lower() == "quit":
            print("再见!")
            break

        print("[INFO] 检索 + 生成中...", end="\r")
        result = qa_chain.invoke({"query": question})

        print(" " * 30, end="\r")
        print(f"\n回答:\n{result['result']}")

        if result.get("source_documents"):
            print("\n参考来源:")
            seen = set()
            for i, doc in enumerate(result["source_documents"], 1):
                source = doc.metadata.get("source", "未知")
                page = doc.metadata.get("page", "?")
                key = f"{source}-{page}"
                if key not in seen:
                    seen.add(key)
                    snippet = doc.page_content[:80].replace("\n", " ")
                    print(f"  [{i}] {os.path.basename(source)} 第{page}页 -> {snippet}...")


def main():
    parser = argparse.ArgumentParser(description="RAG 文档问答系统")
    parser.add_argument("--file", "-f", help="直接指定文档路径，跳过交互式输入")
    parser.add_argument("--reset", action="store_true", help="强制重建向量库")
    _args = parser.parse_args()

    # 强制重建
    if _args.reset and os.path.exists(PERSIST_DIR):
        import shutil
        shutil.rmtree(PERSIST_DIR)
        print("[OK] 已清除旧向量库")

    # 已有向量库时直接加载
    if os.path.exists(PERSIST_DIR) and os.listdir(PERSIST_DIR):
        print(f"[INFO] 检测到已有向量库: {PERSIST_DIR}/")
        choice = input("   直接使用现有向量库? (Y/n): ").strip().lower()
        if choice in ("", "y", "yes"):
            print("[INFO] 加载已有向量库...")
            vectorstore = Chroma(
                persist_directory=PERSIST_DIR,
                embedding_function=embeddings,
            )
            chat_loop(vectorstore)
            return

    # 确定文件路径
    if _args.file:
        file_path = _args.file
    else:
        file_path = input("拖入 PDF 或 TXT 文件路径: ").strip().strip('"').strip("'")

    if not os.path.exists(file_path):
        print(f"[ERROR] 文件不存在: {file_path}")
        sys.exit(1)

    chunks = load_and_split(file_path)
    vectorstore = build_vectorstore(chunks)
    chat_loop(vectorstore)


if __name__ == "__main__":
    main()
