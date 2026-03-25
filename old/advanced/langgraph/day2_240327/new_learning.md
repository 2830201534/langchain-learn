# Day2 · LangGraph 进阶：ConditionalEdge + Cycles + Memory

## 一、条件边详解

### 1.1 为什么需要条件边？

普通边是固定的：A → B
条件边是根据 state 内容决定走向：A → {B / C / D}

### 1.2 三种条件边写法

```python
from typing import Literal

# 方式1：返回字符串（节点名）
def route_v1(state: NL2SQLState) -> Literal["success", "fail"]:
    if state.get("error"):
        return "fail"
    return "success"

# 方式2：返回字符串（节点名）—— 简化版
def route_v2(state: NL2SQLState) -> str:
    return "success" if not state.get("error") else "fail"

# 方式3：字典映射（最灵活）
def route_v3(state: NL2SQLState) -> Literal["generate_sql", "fallback"]:
    intent = state.get("intent", "")
    if intent in ["gmv", "order", "uv"]:
        return "generate_sql"
    return "fallback"

# 注册条件边
graph.add_conditional_edges(
    "parse_intent",           # 起始节点
    route_v3,                 # 路由函数
    {
        "generate_sql": "generate_sql_node",  # intent in [gmv, order, uv] → 这里
        "fallback": "fallback_node"           # 否则 → 这里
    }
)
```

---

## 二、Cycles（循环）：让图可以重复

### 2.1 为什么要循环？

LCEL 管道只能走一次，但实际工作流经常需要**重试**：

```
生成SQL → 执行SQL → 结果校验 → 失败 → 重新生成SQL → ...
```

这就是**循环**：节点之间形成环。

### 2.2 如何创建循环？

关键是：**节点可以指向自己，或指向上游节点**，形成环。

```python
from typing import Literal

class LoopState(TypedDict):
    count: int
    max_retries: int
    error: str | None

def step_a(state: LoopState) -> LoopState:
    return {"count": state["count"] + 1}

def step_b(state: LoopState) -> LoopState:
    if state["count"] < 3:
        return {"error": "需要重试"}
    return {"error": None}

def route_loop(state: LoopState) -> Literal["step_a", "__end__"]:
    """决定是否继续循环"""
    if state["error"] and state["count"] < state["max_retries"]:
        return "step_a"  # 继续循环
    return "__end__"     # 退出

graph = StateGraph(LoopState)
graph.add_node("step_a", step_a)
graph.add_node("step_b", step_b)
graph.add_edge(START, "step_a")
graph.add_edge("step_a", "step_b")
graph.add_conditional_edges(
    "step_b",
    route_loop,
    {"step_a": "step_a", "__end__": END}
)
```

**注意**：`"__end__"` 在条件边中代表结束，而不是 `END` 对象。

### 2.3 SQL 重试循环实战

```python
MAX_RETRIES = 3

class SQLRetryState(TypedDict):
    query: str
    intent: str | None
    sql: str | None
    result: str | None
    error: str | None
    attempt: int

def generate_sql(state: SQLRetryState) -> SQLRetryState:
    """生成SQL（每次尝试不同的SQL）"""
    return {
        "sql": f"SELECT SUM(pay_amount) FROM orders -- attempt {state['attempt']}",
        "attempt": state["attempt"] + 1
    }

def execute_sql(state: SQLRetryState) -> SQLRetryState:
    """执行SQL"""
    # 模拟：attempt=1/2 失败，attempt=3 成功
    if state["attempt"] <= 3:
        return {"error": "SQL syntax error"}
    return {"result": "¥999,999", "error": None}

def route_retry(state: SQLRetryState) -> Literal["generate_sql", "__end__"]:
    """根据是否有错误决定是否重试"""
    if state["error"] and state["attempt"] < MAX_RETRIES:
        return "generate_sql"  # 继续重试
    return "__end__"

graph = StateGraph(SQLRetryState)
graph.add_node("generate_sql", generate_sql)
graph.add_node("execute_sql", execute_sql)
graph.add_edge(START, "generate_sql")
graph.add_edge("generate_sql", "execute_sql")
graph.add_conditional_edges(
    "execute_sql",
    route_retry,
    {"generate_sql": "generate_sql", "__end__": END}
)

app = graph.compile()
result = app.invoke({
    "query": "GMV",
    "intent": "gmv",
    "sql": None,
    "result": None,
    "error": None,
    "attempt": 0
})
print(f"最终SQL: {result['sql']}, 结果: {result['result']}")
```

---

## 三、Memory（状态持久化）

### 3.1 LangGraph 的 Memory 机制

LangGraph 的 Memory 不是 LangChain 的 ConversationMemory，而是**Checkpoint（检查点）**机制：

```python
from langgraph.checkpoint.memory import MemorySaver

# 创建内存检查点
checkpointer = MemorySaver()

# 编译时传入
app = graph.compile(checkpointer=checkpointer)

# 带 thread_id 调用（类似会话ID）
config = {"configurable": {"thread_id": "user_123"}}
result = app.invoke({"query": "GMV"}, config=config)

# 下一个问题，同一个 thread_id，自动恢复历史状态
result2 = app.invoke({"query": "按区域拆一下"}, config=config)
```

### 3.2 Checkpoint 的核心原理

```
Thread ID: "user_123"
├── Turn 1: {"query": "GMV", "intent": "gmv", "sql": "..."}
├── Turn 2: {"query": "按区域拆", "intent": "gmv", "sql": "...", "prev_sql": "..."}
└── Turn 3: {"query": "加环比", "intent": "gmv", "sql": "...", "history": [...]}
```

每个 turn 的 state 都被保存，下次调用同一个 thread_id 时，LangGraph 自动加载历史 state。

### 3.3 多轮 NL2SQL + Checkpoint

```python
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END

class MultiTurnState(TypedDict):
    query: str
    history: list[str]  # 对话历史
    current_sql: str | None
    result: str | None

checkpointer = MemorySaver()
graph = StateGraph(MultiTurnState)
# ... 注册节点和边 ...
app = graph.compile(checkpointer=checkpointer)

# 第一轮
config = {"configurable": {"thread_id": "user_001"}}
r1 = app.invoke({"query": "近7天GMV", "history": [], "current_sql": None, "result": None}, config)
print(r1["result"])  # "¥1,234,567"

# 第二轮（上下文保持）
r2 = app.invoke({"query": "按区域拆一下", "history": r1["history"], "current_sql": r1["current_sql"], "result": None}, config)
print(r2["result"])  # "华东: ¥500k, 华南: ¥300k..."

# 第三轮（引用"刚才的指标"）
r3 = app.invoke({"query": "还是那个GMV，加上环比", "history": r2["history"], "current_sql": r2["current_sql"], "result": None}, config)
```

---

## 四、ConditionalNode 和 Router 模式

### 4.1 路由函数的完整写法

```python
from typing import Literal, Union

def route_intent(state: NL2SQLState) -> Literal["gmv_node", "order_node", "common_node"]:
    """根据意图路由到不同分支"""
    intent = state.get("intent", "")
    mapping = {
        "gmv": "gmv_node",
        "order": "order_node",
        "uv": "order_node"  # uv 和 order 共用同一节点
    }
    return mapping.get(intent, "common_node")
```

### 4.2 多条件组合路由

```python
def route(state: FullState) -> Literal["sql_gen", "api_call", "fallback"]:
    # 组合多个条件
    has_intent = state.get("intent") is not None
    is_complex = state.get("complexity", "low") == "high"
    has_error = state.get("error") is not None

    if has_error:
        return "sql_gen"       # 有错误 → 重新生成
    elif has_intent and not is_complex:
        return "sql_gen"       # 有意图且简单 → 直接生成
    elif has_intent and is_complex:
        return "api_call"     # 复杂查询 → 调用 API
    else:
        return "fallback"      # 无法处理 → 兜底
```

---

## 五、LangGraph 的三大应用场景

| 场景 | 特点 | codex 对应 |
|------|------|-----------|
| **多轮对话 + 上下文** | Checkpoint 做状态持久化 | NL2SQL 多轮追问 |
| **循环重试** | generate → execute → validate → loop | SQL 生成失败重试 |
| **条件分支** | 意图/复杂度/错误决定走向 | RouteDecision 四路路由 |

---

## 六、学习总结

- **条件边**：`add_conditional_edges(起始节点, 路由函数, 映射字典)`
- **循环**：在条件边中返回上游节点名实现环
- **Checkpoint**：`MemorySaver()` + `thread_id` = 有状态的对话
- **`__end__`**：条件边中表示结束（不是 `END` 对象）
- **路由函数**：返回字符串（节点名），决定下一步去哪

---

## 七、下期预告

> Day3 新内容：**实战 + 重构 codex 决策链路**
- 用 LangGraph 重构 RouteDecision
- 输出 codex 重构方案图
- 制定下周末重构 Task List

---

## 八、练习题

1. 实现 SQL 重试循环：`generate → execute → validate`，失败最多重试3次
2. 给 Day1 的 NL2SQL 加上 Checkpoint，实现多轮对话（thread_id 保持上下文）
3. 实现一个"意图路由"条件边：根据 `state["intent"]` 路由到 `gmv_node` / `order_node` / `common_node`
