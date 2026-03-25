# Day1 · LangGraph 基础：StateGraph + Node + Edge

## 一、LangGraph 核心概念

### 1.1 什么是 LangGraph？

LangGraph 是 LangChain 生态中的**有状态工作流引擎**：
- LangChain (LCEL)：线性管道，`A → B → C`
- LangGraph：有向有环图，`A ↔ B → C → A`（可循环）

**三个关键词：** 节点（Node）+ 边（Edge）+ 状态（State）

### 1.2 核心数据结构：State

State 是一个**共享的 dict**，在整个图的生命周期中传递：

```python
from typing import TypedDict
from langgraph.graph import StateGraph, END

class NL2SQLState(TypedDict):
    """NL2SQL 工作流的状态"""
    query: str              # 用户原始查询
    intent: str | None      # 解析出的意图
    sql: str | None         # 生成的 SQL
    result: str | None      # 执行结果
    error: str | None       # 错误信息
    turns: int              # 对话轮次
```

### 1.3 节点（Node）：工作流的每一步

节点是一个 **Python 函数**，接收当前 state，返回更新的 state：

```python
def parse_intent(state: NL2SQLState) -> NL2SQLState:
    """解析用户意图"""
    query = state["query"]
    # 调用 LLM 解析意图...
    intent = "gmv_query"  # 假设解析结果
    return {"intent": intent}
```

### 1.4 边（Edge）：节点之间的连接

两种边：
- **普通边（Normal Edge）**：无条件，从 A 到 B
- **条件边（Conditional Edge）**：根据 state 决定下一步

```python
from langgraph.graph import StateGraph

graph = StateGraph(NL2SQLState)

# 注册节点
graph.add_node("parse_intent", parse_intent)
graph.add_node("generate_sql", generate_sql)

# 普通边：A → B
graph.add_edge("parse_intent", "generate_sql")

# 条件边：根据 intent 判断下一步
def route_by_intent(state: NL2SQLState) -> str:
    if state["intent"] == "gmv_query":
        return "generate_sql"
    else:
        return "fallback"

graph.add_conditional_edges(
    "parse_intent",
    route_by_intent,
    {
        "generate_sql": "generate_sql",
        "fallback": END  # END 是 LangGraph 内置的终止节点
    }
)
```

### 1.5 完整最小示例

```python
from typing import TypedDict
from langgraph.graph import StateGraph, END

# Step 1: 定义 State
class MyState(TypedDict):
    message: str
    count: int

# Step 2: 定义 Node（函数）
def node_a(state: MyState) -> MyState:
    return {"message": state["message"] + " → A", "count": state["count"] + 1}

def node_b(state: MyState) -> MyState:
    return {"message": state["message"] + " → B", "count": state["count"] + 1}

# Step 3: 构建图
graph = StateGraph(MyState)
graph.add_node("node_a", node_a)
graph.add_node("node_b", node_b)
graph.add_edge("node_a", "node_b")    # A → B
graph.add_edge("node_b", END)         # B → 结束

# Step 4: 编译
app = graph.compile()

# Step 5: 运行
result = app.invoke({"message": "Start", "count": 0})
print(result)
# {'message': 'Start → A → B', 'count': 2}
```

---

## 二、LangGraph vs LCEL vs Java 状态机

| 对比项 | LCEL | LangGraph | Java 状态机（Spring StateMachine）|
|--------|------|-----------|---------|
| 拓扑结构 | 线性管道 | 有向有环图 | 有向有环图 |
| 条件分支 | ❌ | ✅ | ✅ |
| 循环 | ❌ | ✅ | ✅ |
| 状态共享 | ❌ | ✅（通过State）| ✅ |
| 人机交互 | ❌ | ✅ | ✅ |
| 并行节点 | ❌ | ✅ | ✅ |

---

## 三、实战：NL2SQL StateGraph（单轮版）

### 3.1 状态定义

```python
from typing import TypedDict, Literal

class NL2SQLState(TypedDict):
    query: str
    intent: str | None
    sql: str | None
    result: str | None
    error: str | None
    should_retry: bool
```

### 3.2 节点定义

```python
def parse_intent(state: NL2SQLState) -> NL2SQLState:
    """节点1：解析意图"""
    from langchain_openai import ChatOpenAI
    from langchain_core.output_parsers import JsonOutputParser
    from pydantic import BaseModel

    class Intent(BaseModel):
        metric: str
        time_range: str
        aggregation: str

    llm = ChatOpenAI(model="MiniMax-M2.7", api_key=get_pass(), base_url="https://api.minimaxi.com/v1")

    prompt = f"""分析查询，提取指标和时间范围。
    查询：{state['query']}
    表：orders(id, user_id, pay_amount, status, created_at)
    只输出JSON："""

    from langchain_core.messages import HumanMessage
    response = llm.invoke([HumanMessage(content=prompt)])
    # 解析 response.content 为 Intent 对象...
    return {"intent": "gmv_query"}  # 简化

def generate_sql(state: NL2SQLState) -> NL2SQLState:
    """节点2：生成SQL"""
    return {"sql": "SELECT SUM(pay_amount) FROM orders WHERE status='paid' AND created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)"}

def execute_sql(state: NL2SQLState) -> NL2SQLState:
    """节点3：执行SQL（模拟）"""
    return {"result": "¥1,234,567.89"}

def format_response(state: NL2SQLState) -> NL2SQLState:
    """节点4：格式化输出"""
    return {"result": f"近7天 GMV 为 {state['result']}"}
```

### 3.3 构建图

```python
from langgraph.graph import StateGraph, END, START

graph = StateGraph(NL2SQLState)

# 注册节点
graph.add_node("parse_intent", parse_intent)
graph.add_node("generate_sql", generate_sql)
graph.add_node("execute_sql", execute_sql)
graph.add_node("format_response", format_response)

# 边
graph.add_edge(START, "parse_intent")
graph.add_edge("parse_intent", "generate_sql")
graph.add_edge("generate_sql", "execute_sql")
graph.add_edge("execute_sql", "format_response")
graph.add_edge("format_response", END)

# 编译
app = graph.compile()

# 运行
result = app.invoke({"query": "近7天GMV是多少", "intent": None, "sql": None, "result": None, "error": None, "should_retry": False})
```

---

## 四、LangGraph 的内置节点

LangGraph 提供两个特殊节点：

```python
from langgraph.graph import START, END

graph.add_edge(START, "first_node")  # START 是入口节点
graph.add_edge("last_node", END)    # END 是终止节点
```

---

## 五、学习总结

- **State**：共享的 TypedDict，整个图的上下文
- **Node**：Python 函数，接收 State，返回 State
- **Edge**：连接节点，`add_edge` 是无条件，`add_conditional_edges` 是条件分支
- **START/END**：内置入口和终止节点
- **compile()**：将图编译成可执行的 App

## 六、下期预告

> Day2 新内容：**ConditionalEdge + Cycles + 多轮对话**
- 如何让图循环？（实现"SQL不对 → 重新生成"）
- Memory 如何接入 LangGraph？
- 实战：多轮 NL2SQL 状态机

## 七、练习题

1. 用 StateGraph 实现一个三节点流程：`输入 → 大写转换 → 输出`
2. 给上面的流程加一个条件边：如果输入包含"退出"，则直接结束
3. 画出你自己的 NL2SQL StateGraph 的节点和边（手画或 ASCII 图）
