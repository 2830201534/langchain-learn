# Day5 练习题：Agent + RAG

> 🎯 练习目标：掌握 Agent 决策循环，理解 RAG 检索增强原理
> ⏰ 预计时间：60~90 分钟
> 📝 要求：所有代码必须实际运行

---

## 练习1：定义 Tool 并测试（⭐⭐）
**目标**：掌握 @tool 装饰器的使用

```python
from langchain.tools import tool

@tool
def get_gmv(days: int) -> str:
    """查询近N天的GMV数据
    
    Args:
        days: 天数，如7表示近7天
    Returns:
        GMV数据字符串
    """
    return f"近{days}天 GMV: ¥{days * 50000:,.2f}"
```

**任务**：
1. 新建文件 `practice_01_tool_basics.py`
2. 定义 3 个 Tool：
   - `get_gmv(days)` - 查询GMV
   - `get_orders(days)` - 查询订单数
   - `calculate(expr)` - 数学计算
3. 测试每个 Tool 的调用

---

## 练习2：Functions Agent 完整调用（⭐⭐⭐）
**目标**：掌握 Agent 的创建和调用流程

**任务**：
1. 新建文件 `practice_02_functions_agent.py`
2. 构建完整的 Functions Agent：
   - 使用练习1的3个 Tool
   - 创建 AgentExecutor
   - 测试不同类型的问题（数据查询 / 数学计算 / 通用问题）

**验收标准**：
- Agent 能正确选择调用哪个 Tool
- Tool 参数正确传递
- 最终返回自然语言结果

---

## 练习3：Agent 决策过程解析（⭐⭐⭐）
**目标**：理解 Agent 的"思考 → 行动 → 观察"循环

**任务**：
1. 新建文件 `practice_03_agent_loop.py`
2. 设置 `verbose=True`
3. 观察 Agent 的决策输出，理解每一步

```python
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True  # 打印完整决策过程
)
```

---

## 练习4：带 Memory 的 Agent（⭐⭐⭐⭐）
**目标**：掌握多轮 Agent 对话

**任务**：
1. 新建文件 `practice_04_agent_memory.py`
2. 实现多轮对话：

```
第1轮：用户 → "查一下近7天GMV"
第2轮：用户 → "按区域拆一下"
第3轮：用户 → "还是刚才那个指标，加上环比"
```

3. 验证 Agent 能否理解上下文

---

## 练习5：FAISS 向量数据库构建（⭐⭐⭐⭐）
**目标**：掌握文档向量化的流程

**任务**：
1. 新建文件 `practice_05_faiss_vectorstore.py`
2. 构建 FAISS 向量数据库：

```python
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS

# 1. 准备文档
docs = [
    "GMV定义：SUM(pay_amount)，过滤条件：status='paid'",
    "订单数量：COUNT(id)，无过滤条件",
    "用户数量：COUNT(DISTINCT user_id)，无过滤条件"
]

# 2. 向量化
embeddings = OpenAIEmbeddings(model="text-embedding-ada-002", api_key=get_pass())
db = FAISS.from_texts(docs, embeddings)

# 3. 相似度检索
results = db.similarity_search("GMV怎么算", k=2)
for doc in results:
    print(doc.page_content)
```

---

## 练习6：完整 RAG Chain 构建（⭐⭐⭐⭐）
**目标**：掌握 RAG 的完整流程

**任务**：
1. 新建文件 `practice_06_rag_chain.py`
2. 实现完整的 RAG Chain：

```
用户问题 → Embedding → FAISS检索 → 拼接Prompt → LLM生成回答
```

3. 测试不同类型的问题

---

## 练习7：挑战题 - NL2SQL Agent（⭐⭐⭐⭐⭐）
**目标**：综合运用 Agent + Tool + Memory

**任务**：
1. 新建文件 `practice_07_nl2sql_agent.py`
2. 构建一个智能 NL2SQL Agent：

```python
tools = [
    # Tool 1: NL2SQL（自然语言→SQL）
    Tool(name="nl2sql", func=nl2sql_func, description="将自然语言转SQL"),
    # Tool 2: QuerySQL（执行SQL）
    Tool(name="query_sql", func=query_sql_func, description="执行SQL并返回结果")
]

# Agent 决策流程：
# 1. 用户问"近7天GMV是多少"
# 2. Agent 调用 nl2sql → 生成 SQL
# 3. Agent 调用 query_sql → 执行 SQL
# 4. Agent 返回自然语言结果
```

3. 实现多轮对话能力

---

## 练习8：挑战题 - RAG + Memory 整合（⭐⭐⭐⭐⭐）
**目标**：实现带知识库检索和多轮记忆的完整系统

**任务**：
1. 新建文件 `practice_08_rag_memory.py`
2. 实现：
   - RAG 知识库检索
   - Memory 多轮对话
   - Agent 自主决策使用哪个能力

---

## 输出要求

完成后记录：
1. Agent 决策循环的理解
2. RAG 和 Agent 的区别与联系
3. 多轮对话 + RAG 的应用场景思考
