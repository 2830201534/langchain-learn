# Day5 复习文档：Agent + RAG

> 📅 复习日期：3月28日（Agent + RAG 强化复习）
> 🎯 复习目标：理解 Agent 决策循环，掌握 RAG 检索原理

---

## 一、Agent 核心原理

### 1.1 Agent vs Chain
- **Chain**：固定流程，Prompt → LLM → Output，一步接一步
- **Agent**：模型自主决策，动态选择下一步做什么

### 1.2 Agent 工作循环
```
用户问题
    ↓
[思考] LLM 分析：需要调用什么工具？
    ↓
[决策] 选择 Tool（或直接回答）
    ↓
[行动] 执行 Tool，返回结果
    ↓
[观察] 获取 Tool 输出
    ↓
[循环] 回到 [思考]，直到得到答案
```

---

## 二、Tool 定义

```python
from langchain.tools import tool

@tool
def get_gmv(days: int) -> str:
    """查询近N天的GMV数据
    
    Args:
        days: 天数
    Returns:
        GMV数据
    """
    return f"近{days}天 GMV: ¥{days * 50000:,.2f}"
```

**三个关键要素：**
- `name`：工具名称
- `description`：描述（LLM 靠这个理解什么时候调用）
- `args`：参数定义

---

## 三、Functions Agent

```python
from langchain.agents import AgentExecutor, create_openai_functions_agent

# 创建 Agent
agent = create_openai_functions_agent(llm, tools, prompt)

# 创建 Executor
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True  # 打印决策过程
)

# 调用
result = agent_executor.invoke({"input": "近7天GMV是多少？"})
```

---

## 四、带 Memory 的 Agent

```python
memory = ConversationBufferMemory(memory_key="chat_history")

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    memory=memory  # 支持多轮对话
)
```

---

## 五、RAG 原理

### 5.1 什么是 RAG？
Retrieval Augmented Generation = 检索 + 生成
解决 LLM"不知道私域数据"的问题

### 5.2 RAG 流程
```
用户问题
    ↓
[Embedding] 向量化
    ↓
[VectorStore] 相似度检索
    ↓
[Context] 拼接检索结果到 Prompt
    ↓
[LLM] 生成回答
```

---

## 六、RAG 核心组件

| 组件 | 作用 |
|------|------|
| Document Loader | 加载文档 |
| Text Splitter | 分块处理 |
| Embeddings | 向量化模型 |
| VectorStore | 向量数据库（FAISS） |
| Retriever | 检索器 |
| Chain | 组合链条 |

---

## 七、FAISS + RetrievalQA

```python
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA

# 存入向量数据库
db = FAISS.from_texts(docs, embeddings)

# 创建检索器
retriever = db.as_retriever(search_kwargs={"k": 2})

# 构建 RAG Chain
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever
)
```

---

## 八、Agent vs RAG 区别

| 维度 | Agent | RAG |
|------|-------|-----|
| 核心能力 | 工具调用 | 知识检索 |
| 数据来源 | 工具执行结果 | 向量数据库 |
| 决策方式 | LLM 自主决策 | 相似度匹配 |
| 典型场景 | 执行动作 | 回答问题 |

**可以组合：Agent + RAG = 更强大的助手**

---

## 九、自测问题

1. Agent 的"思考"过程本质是什么？
2. Tool 的 description 为什么很重要？
3. FAISS 检索的 `k=2` 是什么意思？
4. RAG 为什么能解决 LLM 知识过时问题？

---

## 十、知识关联

```
                    ┌─────────────────┐
                    │   用户问题       │
                    └────────┬────────┘
                             ↓
              ┌───────────────┴───────────────┐
              ↓                               ↓
        [Agent]                          [RAG]
         ↓                                   ↓
    Tool 调用                          向量检索
         ↓                                   ↓
    执行结果                          拼接 Context
         └───────────────┬───────────────┘
                         ↓
                    [LLM 生成]
                         ↓
                   [最终回答]
```

---

## 十一、本周学习总结

### Day1~5 核心收获
1. **Models**：LLM 调用方式（invoke/stream/batch）
2. **LCEL**：`|` 管道串联，统一 Runnable 接口
3. **Memory**：多轮对话的记忆机制
4. **Agent**：自主决策 + 工具调用
5. **RAG**：检索增强 + 知识库

### 关键理解
- LCEL 是 LangChain 的**编排层**
- Memory 是 LangChain 的**记忆层**
- Agent 是 LangChain 的**决策层**
- RAG 是 LangChain 的**知识层**
