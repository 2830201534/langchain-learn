# Day4 练习题：RAG（检索增强生成）

> 🎯 练习目标：掌握文档切分 → 向量入库 → 检索 → 生成的完整 RAG 链路
> ⏰ 预计时间：60 分钟
> 📝 要求：所有代码必须实际运行

---

## 练习1：文档切分（⭐⭐）
**目标**：掌握 `RecursiveCharacterTextSplitter` 的用法

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

text = """LangChain 是一个用于开发 LLM 应用的框架。
它简化了从开发到生产的全流程。
支持 Python 和 JavaScript。
核心模块包括：Models、Chains、Memory、Agents、Tools。"""

splitter = RecursiveCharacterTextSplitter(
    chunk_size=50,
    chunk_overlap=10,
    separators=["\n", "。", "，", ""]
)

chunks = splitter.split_text(text)
for i, chunk in enumerate(chunks):
    print(f"Chunk {i}: {chunk}")
```

**任务**：新建 `practice_01_text_splitter.py`：
1. 用上面的文本运行，查看切分结果
2. 调整 `chunk_size` 和 `chunk_overlap`，观察变化
3. 用 `["\n\n", "\n", " "] ` 作为分隔符，对比结果

---

## 练习2：FAISS 向量数据库（⭐⭐⭐）
**目标**：掌握 FAISS 的 `from_texts` + `similarity_search`

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from comm.get_pass import get_pass
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS

docs = [
    "GMV定义：SUM(pay_amount)，过滤条件：status='paid'",
    "订单数定义：COUNT(id)，无过滤",
    "UV定义：COUNT(DISTINCT user_id)，无过滤",
    "转化率定义：订单数 / UV * 100%",
    "平均客单价定义：GMV / 订单数"
]

embeddings = OpenAIEmbeddings(
    model="text-embedding-ada-002",
    api_key=get_pass()
)

# 入库
db = FAISS.from_texts(docs, embeddings)

# 保存
db.save_local("faiss_index")

# 查询测试
results = db.similarity_search("GMV怎么算的", k=2)
for doc in results:
    print(doc.page_content)
```

**任务**：新建 `practice_02_faiss_basic.py`，运行并测试：
1. 检索"GMV的口径"
2. 检索"客单价"
3. 用 `similarity_search_with_score` 看相似度分数

---

## 练习3：RetrievalQA Chain（⭐⭐⭐）
**目标**：把检索和问答串成完整链路

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from comm.get_pass import get_pass
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

llm = ChatOpenAI(model="MiniMax-M2.7", api_key=get_pass(), base_url="https://api.minimaxi.com/v1")
embeddings = OpenAIEmbeddings(model="text-embedding-ada-002", api_key=get_pass())

# 加载 FAISS 索引（用练习2的）
db = FAISS.load_local("faiss_index", embeddings)

# 构建 RetrievalQA
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=db.as_retriever(search_kwargs={"k": 3}),
    return_source_documents=True
)

# 测试
result = qa_chain.invoke({"query": "GMV的口径是什么？过滤条件是什么？"})
print("回答：", result["result"])
print("\n参考文档：")
for doc in result["source_documents"]:
    print("-", doc.page_content)
```

**任务**：新建 `practice_03_retrieval_qa.py`，测试：
1. "GMV的口径是什么"
2. "订单数需要过滤条件吗"
3. "转化率怎么算"

---

## 练习4：对比四种 chain_type（⭐⭐⭐⭐）
**目标**：理解 `stuff` / `map_reduce` / `refine` / `map_rerank` 的区别

```python
from langchain.chains import RetrievalQA

chain_types = ["stuff", "map_reduce", "refine"]

for chain_type in chain_types:
    qa = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type=chain_type,
        retriever=db.as_retriever()
    )
    result = qa.invoke({"query": "GMV的定义"})
    print(f"\n=== {chain_type} ===")
    print(result["result"])
```

**任务**：新建 `practice_04_chain_type_compare.py`，运行并对比四种模式的输出差异。

---

## 练习5：构建 codex 指标知识库 RAG（⭐⭐⭐⭐）
**目标**：综合实战，用 codex 的指标定义构建知识库

**任务**：新建 `practice_05_codex_rag.py`：

1. 定义 codex 指标知识：
```python
codex_metrics = [
    "GMV（成交总额）：SUM(pay_amount)，过滤条件 status='paid'，时间范围默认近7天",
    "订单数：COUNT(id)，无过滤条件",
    "UV（独立访客数）：COUNT(DISTINCT user_id)，无过滤条件",
    "转化率：订单数 / UV * 100%，反映流量到订单的转化效率",
    "平均客单价：GMV / 订单数，衡量用户消费水平",
    "复购率：回头客订单数 / 总订单数 * 100%",
]
```

2. 构建 FAISS 向量库
3. 构建 RetrievalQA Chain
4. 测试多轮对话：
```
第1轮："GMV的口径是什么？"
第2轮："那转化率呢？"
第3轮："我还想知道平均客单价的定义"
```

---

## 输出要求

完成后在 `practice_summary.md` 中记录：
1. TextSplitter 的 `chunk_size` 和 `chunk_overlap` 如何调优？
2. 四种 `chain_type` 的适用场景？
3. RAG 和普通 LLM 回答相比，优势在哪里？
