# Day4 学习内容：RAG（检索增强生成）

## 一、为什么需要 RAG？

**问题**：LLM 的知识有截止日期，私域数据（如 codex 的指标定义）它不知道。

**解决**：RAG = Retrieval（检索）+ Augmented（增强）+ Generation（生成）

```
用户问题 → 检索私域知识 → 拼接进 Prompt → LLM 生成回答
```

---

## 二、RAG 核心流程（4步）

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  文档切分   │ →  │  向量入库    │ →  │  相似度检索  │ →  │  增强生成   │
│ TextSplitter│    │  FAISS/Milvus│    │ similarity  │    │  LLM + Context│
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

---

## 三、文档切分（TextSplitter）

### 3.1 为什么要切分？

- LLM context window 有限
- 匹配粒度：切太小丢失语义，切太大引入噪声

### 3.2 RecursiveCharacterTextSplitter

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,        # 每段最大字符数
    chunk_overlap=50,      # 段之间重叠 50 字符（保持上下文）
    separators=["\n\n", "\n", "。", "！", "？", ""]  # 分隔符优先级
)

docs = splitter.split_text(long_text)
```

### 3.3 按文件批量切分

```python
from langchain.document_loaders import TextLoader

loader = TextLoader("codex_metrics.md")
documents = loader.load()
splits = splitter.split_documents(documents)
```

---

## 四、向量数据库

### 4.1 向量化的原理

```
文本 → Embedding Model → 向量（e.g. 1536维）→ 存入向量库
```

### 4.2 FAISS（Facebook AI Similarity Search）

```python
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS

# 1. 向量化
embeddings = OpenAIEmbeddings(model="text-embedding-ada-002", api_key=get_pass())

# 2. 入库
db = FAISS.from_texts(docs, embeddings)

# 3. 保存到磁盘
db.save_local("faiss_index")

# 4. 加载
db = FAISS.load_local("faiss_index", embeddings)
```

### 4.3 相似度检索

```python
# 单一查询
results = db.similarity_search("GMV的口径是什么", k=3)
for doc in results:
    print(doc.page_content)

# 带相似度分数
results = db.similarity_search_with_score("GMV的口径是什么", k=3)
for doc, score in results:
    print(f"[{score:.3f}] {doc.page_content}")
```

---

## 五、RetrievalQA Chain

### 5.1 什么是 RetrievalQA？

把"检索"和"问答"串成一条链：

```python
from langchain.chains import RetrievalQA

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",      # stuff / map_reduce / refine
    retriever=db.as_retriever(search_kwargs={"k": 3}),
    return_source_documents=True
)

result = qa_chain.invoke({"query": "GMV的口径是什么"})
print(result["result"])
```

### 5.2 四种 chain_type 对比

| 类型 | 原理 | 适用场景 |
|------|------|---------|
| `stuff` | 把所有文档塞进一个 prompt | 文档少（<5） |
| `map_reduce` | 每个文档单独总结，再汇总 | 文档多 |
| `refine` | 逐轮迭代优化答案 | 答案需要精炼 |
| `map_rerank` | 每个文档打分，取最高 | 精确匹配 |

---

## 六、实战：基于 codex 指标定义的 RAG

### 6.1 构建知识库

```python
# 假设 codex_metrics.md 内容：
# - GMV：SUM(pay_amount)，过滤 status='paid'
# - 订单数：COUNT(id)，无过滤
# - UV：COUNT(DISTINCT user_id)，无过滤

docs = [
    "GMV指标定义：GMV = SUM(pay_amount)，过滤条件：status='paid'，时间范围默认近7天",
    "订单数指标定义：订单数 = COUNT(id)，无过滤条件",
    "UV指标定义：UV = COUNT(DISTINCT user_id)，无过滤条件"
]

# 入库
db = FAISS.from_texts(docs, embeddings)
```

### 6.2 完整 RAG Chain

```python
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=db.as_retriever(search_kwargs={"k": 2})
)

# 测试
questions = [
    "GMV的口径是什么？",
    "订单数怎么算的？",
    "UV指标需要过滤条件吗？"
]

for q in questions:
    result = qa_chain.invoke({"query": q})
    print(f"Q: {q}\nA: {result['result']}\n")
```

### 6.3 结果示例

```
Q: GMV的口径是什么？
A: GMV = SUM(pay_amount)，过滤条件是 status='paid'

Q: 订单数怎么算的？
A: 订单数 = COUNT(id)，无过滤条件
```

---

## 七、RAG 的局限性

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| 检索不准 | Embedding 模型质量差 | 换更好的 Embedding |
| 上下文太长 | 检索到太多文档 | 调整 k 值 / chunk_size |
| 幻觉 | LLM 乱编 | 增加 Prompt 约束 |
| 实时性 | 知识库静态 | 定期更新向量库 |

---

## 八、与 codex 的对应关系

| RAG 概念 | codex 对应 |
|---------|-----------|
| TextSplitter | `SemanticQueryCatalogSnapshot` 文档解析 |
| FAISS / 向量库 | 指标定义的向量索引 |
| RetrievalQA | NL2SQL 的 Context 构建 |
| 知识库 | codex 的 metric / dimension / entity 元数据 |

---

## 九、下期预告

> Day5 新内容：**Agent（自主决策）**
- Tool Calling 是什么？
- Agent 循环：模型决定 → 调用工具 → 返回结果 → 再决定
- 对应 codex 的 RouteDecision（四路路由）
