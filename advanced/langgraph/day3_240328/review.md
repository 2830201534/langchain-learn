# Day3 复习文档：LangGraph 重构 codex 决策链路

> 📅 复习日期：3月28日
> 🎯 复习目标：巩固 LangGraph 核心概念，建立与 codex 的关联

---

## 一、LangGraph 三大核心

### 1. State（状态）
```python
class MyState(TypedDict):
    query: str
    result: str | None
    attempt: int
```
- 整个图生命周期中**共享的字典**
- 每个节点接收并返回更新后的 State

### 2. Node（节点）
```python
def my_node(state: MyState) -> MyState:
    return {"result": state["query"].upper()}
```
- **Python 函数**
- 接收当前 State，返回更新的 State

### 3. Edge（边）
```python
# 普通边
graph.add_edge("node_a", "node_b")

# 条件边
graph.add_conditional_edges("node_a", route_fn, {"go_b": "node_b", "go_c": "node_c"})
```
- 普通边：固定走向
- 条件边：根据 State 内容动态决定走向

---

## 二、条件边路由函数写法

```python
from typing import Literal

def route(state: MyState) -> Literal["node_b", "node_c"]:
    if state["value"] > 10:
        return "node_b"
    return "node_c"
```

- **返回类型**：`Literal["节点A", "节点B", ...]`
- **返回值**：目标节点的**名字符串**

---

## 三、Cycles（循环）写法

```python
def retry_route(state: MyState) -> Literal["generate_sql", "__end__"]:
    if state.get("error") and state["attempt"] < state["max_retries"]:
        return "generate_sql"  # 循环回去
    return "__end__"           # 结束

graph.add_conditional_edges(
    "execute_node",
    retry_route,
    {"generate_sql": "generate_sql", "__end__": END}
)
```

**关键**：
- `__end__` 在条件边中表示结束
- `END` 对象在普通边中表示结束

---

## 四、Checkpoint（状态持久化）

```python
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()
app = graph.compile(checkpointer=checkpointer)

config = {"configurable": {"thread_id": "user_001"}}
result = app.invoke({"query": "GMV"}, config=config)
```

- 不同 `thread_id` = 不同会话
- 同一 `thread_id` 自动恢复历史状态

---

## 五、codex 重构架构速记

```
NL2SQL State
    ├── query / intent / sql / result / response
    ├── attempt / max_retries
    └── validation_result / policy_result

四路路由节点：
    gmv_sql_node / order_sql_node / uv_sql_node / common_sql_node

核心循环：
    generate_sql → validate_and_execute → [error?] → retry_route
                                                      ↓ yes
                                                   generate_sql
                                                      ↓ no
                                                      END
```

---

## 六、自测问题

1. `add_edge` 和 `add_conditional_edges` 的区别？
2. `__end__` 和 `END` 在使用场景上的区别？
3. LangGraph 中实现循环需要什么条件？
4. Checkpointer 的 `thread_id` 作用是什么？
5. 条件边中路由函数的返回类型是什么？

---

## 七、codex 重构 Task List

### P0
- [ ] RouteDecision → StateGraph 节点
- [ ] Checkpointer 多轮对话
- [ ] LangSmith 配置

### P1
- [ ] SQL 重试循环（≤3次）
- [ ] M4 PolicyService 接入
- [ ] M7 LLM 审查节点
