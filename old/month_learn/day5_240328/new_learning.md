# Day5 学习内容：Agent（自主决策）+ RAG（检索增强）

## 一、Agent 是什么？
### 1.1 从 if-else 到 Agent
- 传统路由：硬编码 if-else 逻辑
- Agent：模型自主决定下一步行动
- 本质：让 LLM 拥有"思考能力"

### 1.2 Agent 工作流程
```
用户问题 → [思考] → [决策] → [行动] → [观察] → [思考] → ... → 最终回答
           ↑_______________________________________↓
                        （循环直到得到答案）
```

### 1.3 关键词解释
- **Tool（工具）**：Agent 可以调用的外部能力（搜索、数据库查询、计算器）
- **Action（行动）**：Agent 决定执行的具体动作
- **Observation（观察）**：执行动作后的返回结果
- **AgentExecutor**：Agent 的运行循环引擎

## 二、Tool（工具）— Agent 的手脚
### 2.1 @tool 装饰器
```python
from langchain.tools import tool

@tool
def get_weather(city: str) -> str:
    """查询城市天气
    
    Args:
        city: 城市名称，如"南京"
    Returns:
        天气信息字符串
    """
    return f"{city}今天晴天，温度20-25度"
```

### 2.2 Tool 的核心要素
- **name**：工具名称（Agent 用来决定调用哪个）
- **description**：工具描述（LLM 理解工具用途的关键）
- **args**：参数定义（LLM 生成参数依据）

### 2.3 更多 Tool 示例
```python
@tool
def query_gmv(days: int) -> str:
    """查询近N天的GMV数据
    
    Args:
        days: 天数，如7表示近7天
    Returns:
        GMV数据字符串
    """
    return f"近{days}天 GMV: ¥{days * 50000:,.2f}"

@tool
def calculate(expr: str) -> str:
    """数学计算器
    
    Args:
        expr: Python数学表达式，如 "100+200*3"
    Returns:
        计算结果
    """
    try:
        result = eval(expr)
        return f"计算结果: {result}"
    except:
        return "计算错误"
```

## 三、Functions Agent（OpenAI Functions Agent）
### 3.1 什么是 Functions Agent？
- 利用模型的 function calling 能力
- 模型原生支持工具选择，决策更准确
- LangChain 推荐的使用方式

### 3.2 完整示例
```python
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import tool

llm = ChatOpenAI(model="MiniMax-M2.7", api_key=get_pass(), base_url="https://api.minimaxi.com/v1")

# 定义 Tools
@tool
def get_gmv(days: int) -> str:
    """查询近N天的GMV数据"""
    return f"近{days}天 GMV: ¥{days * 50000:,.2f}"

@tool
def get_order_count(days: int) -> str:
    """查询近N天的订单数量"""
    return f"近{days}天 订单数: {days * 1000:,}"

tools = [get_gmv, get_order_count]

# 创建 Prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个智能数据查询助手，可以帮助用户查询业务数据。"),
    MessagesPlaceholder(variable_name="chat_history", optional=True),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad")
])

# 创建 Agent
agent = create_openai_functions_agent(llm, tools, prompt)

# 创建 Executor
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True
)

# 测试
result = agent_executor.invoke({"input": "近7天GMV是多少？"})
print(result["output"])
```

### 3.3 Agent 决策过程解析（verbose=True 输出示例）
```
>>> 近7天GMV是多少？
思考：用户想查GMV数据，我需要调用get_gmv工具，参数是days=7
行动：调用get_gmv(days=7)
观察：近7天 GMV: ¥350,000.00
思考：已获取数据，可以回答用户了
最终回答：近7天GMV是¥350,000.00
```

## 四、Agent 的决策循环详解
### 4.1 循环步骤
1. **思考（Thought）**：LLM 分析当前情况，决定是否需要行动
2. **行动（Action）**：执行 Tool 或直接回答
3. **观察（Observation）**：获取 Tool 返回结果
4. **循环**：回到步骤1，直到得到最终答案

### 4.2 带 Memory 的 Agent
```python
from langchain.memory import ConversationBufferMemory

memory = ConversationBufferMemory(memory_key="chat_history")

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    memory=memory  # 支持多轮对话
)

# 多轮对话
result = agent_executor.invoke({"input": "查一下近7天GMV"})
result = agent_executor.invoke({"input": "按区域拆一下"})  # 能记住上下文
```

## 五、实战：构建数据查询 Agent（Codex 风格）
```python
"""
实战：构建 NL2SQL 数据查询 Agent
类似 Codex 的 RouteDecision，但用 Agent 实现
"""
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import tool

llm = ChatOpenAI(model="MiniMax-M2.7", api_key=get_pass(), base_url="https://api.minimaxi.com/v1")

@tool
def query_sql(sql: str) -> str:
    """执行SQL查询（模拟）
    
    Args:
        sql: SQL语句
    Returns:
        查询结果
    """
    # 实际项目：调用真实数据库
    if "SUM" in sql and "pay_amount" in sql:
        return '[{"gmv": 1234567.89}]'
    elif "COUNT" in sql:
        return '[{"count": 5678}]'
    return "[]"

@tool
def nl2sql(nl_query: str) -> str:
    """将自然语言转换成SQL
    
    Args:
        nl_query: 自然语言查询，如"近7天GMV是多少"
    Returns:
        SQL语句
    """
    # 实际项目：调用 NL2SQL Chain
    if "GMV" in nl_query or "成交" in nl_query:
        if "7天" in nl_query or "近7" in nl_query:
            return "SELECT SUM(pay_amount) FROM orders WHERE status='paid' AND created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)"
        return "SELECT SUM(pay_amount) FROM orders WHERE status='paid'"
    return "SELECT COUNT(*) FROM orders"

tools = [nl2sql, query_sql]

prompt = ChatPromptTemplate.from_messages([
    ("system", """你是一个智能数据查询助手。
你有两个工具可用：
- nl2sql: 将自然语言转换成SQL
- query_sql: 执行SQL并返回结果

工作流程：
1. 用 nl2sql 把用户问题转成 SQL
2. 用 query_sql 执行 SQL
3. 返回自然语言结果"""),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad")
])

agent = create_openai_functions_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

result = agent_executor.invoke({"input": "近7天GMV是多少？"})
```

## 六、RAG 是什么？
### 6.1 背景问题
- LLM 的知识有截止日期
- LLM 不知道私域数据（内部报表、私有知识库）
- RAG = Retrieval Augmented Generation（检索增强生成）

### 6.2 RAG 流程
```
用户问题 → [检索] → 找到相关文档 → [生成] → LLM生成回答
                    ↑
            知识库（向量数据库）
```

### 6.3 核心组件
- **Document Loader**：加载文档
- **Text Splitter**：分块处理
- **Embeddings**：向量化
- **VectorStore**：向量数据库
- **Retriever**：检索器
- **Chain**：组合链条

## 七、RAG 实战：构建指标定义问答系统
```python
"""
实战：基于 Codex 指标定义的 RAG 问答
场景：用户问"GMV的口径是什么"，从知识库检索回答
"""
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter

llm = ChatOpenAI(model="MiniMax-M2.7", api_key=get_pass(), base_url="https://api.minimaxi.com/v1")

# 1. 准备知识库文档（Codex 指标定义）
knowledge_base = [
    "GMV定义：SUM(pay_amount)，过滤条件：status='paid'",
    "订单数量定义：COUNT(id)，无过滤条件",
    "用户数量定义：COUNT(DISTINCT user_id)，无过滤条件",
    "客单价定义：SUM(pay_amount)/COUNT(id)，过滤条件：status='paid'",
    "退款率定义：COUNT(refund_id)/COUNT(id)，过滤条件：status='refunded'"
]

# 2. 向量化并存入 FAISS
embeddings = OpenAIEmbeddings(model="text-embedding-ada-002", api_key=get_pass())
db = FAISS.from_texts(knowledge_base, embeddings)

# 3. 创建检索器
retriever = db.as_retriever(search_kwargs={"k": 2})  # 返回 top 2

# 4. 构建 RAG Chain
custom_prompt = PromptTemplate(
    template="""基于以下指标定义知识库，回答用户问题。

知识库：
{context}

问题：{question}

要求：
1. 只根据知识库中的定义回答
2. 回答要包含计算公式和过滤条件
3. 如果知识库中没有相关信息，说明不知道

回答：""",
    input_variables=["context", "question"]
)

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",  # 将检索到的文档拼接到 prompt
    retriever=retriever,
    prompt=custom_prompt,
    return_source_documents=True
)

# 5. 测试
result = qa_chain.invoke({"query": "GMV的口径是什么？"})
print(result["result"])
```

## 八、LangChain RAG 流程图
```
                    用户问题
                        ↓
                [Embedding模型]
                        ↓
                   向量查询
                        ↓
            ┌─────────┴─────────┐
            ↓                   ↓
      [FAISS检索器]      [VectorStore]
            ↓                   ↓
      [相关文档块]      [文档数据库]
            └─────────┬─────────┘
                      ↓
              [拼入Prompt]
                      ↓
                   [LLM生成]
                      ↓
                   最终回答
```

## 九、RAG vs Fine-tuning 选择
| 维度 | RAG | Fine-tuning |
|------|-----|------------|
| 知识更新 | 实时，更改文档即可 | 需要重新训练 |
| 成本 | 低，无需训练 | 高，GPU训练费用 |
| 准确性 | 取决于检索质量 | 取决于训练数据 |
| 适用场景 | 动态知识库 | 固定模式/风格 |

## 十、学习总结
- Agent = 思考 + 决策 + 行动 + 观察的循环
- @tool 定义工具，Agent 自主选择调用
- Functions Agent 是推荐方式
- RAG = 检索 + 生成，解决知识不足问题
- FAISS 是常用向量数据库

## 十一、下期预告
- Day6：全链路综合实战 + 架构设计
- 预告：如何用 LangChain 重构 Codex NL2SQL 系统？
