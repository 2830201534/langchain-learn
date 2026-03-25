# Day2 练习题：ConditionalEdge + Cycles + Memory

> 🎯 练习目标：掌握条件路由、循环重试、Checkpoint 持久化
> ⏰ 预计时间：75 分钟

---

## 练习1：SQL 重试循环（⭐⭐⭐）
**目标**：实现 `生成SQL → 执行 → 失败重试（最多3次）` 的循环

**State**：
```python
class RetryState(TypedDict):
    query: str
    sql: str | None
    result: str | None
    error: str | None
    attempt: int
    max_retries: int
```

**流程**：
```
START → generate_sql → execute_sql → [有错误?] → yes → generate_sql (循环)
                                      ↓ no
                                     END
```

```python
from typing import Literal

def route_after_execute(state: RetryState) -> Literal["generate_sql", "__end__"]:
    """根据是否有错误决定是否重试"""
    if state.get("error") and state["attempt"] < state["max_retries"]:
        return "generate_sql"
    return "__end__"

# 提示：
# 1. generate_sql 里 attempt += 1
# 2. execute_sql 模拟：attempt < 3 时返回 error，attempt >= 3 时返回成功
```

**任务**：新建 `practice_01_retry_loop.py`，打印每次 attempt 的结果，验证循环是否工作。

---

## 练习2：意图路由 - 三个分支（⭐⭐⭐）
**目标**：掌握多分支条件边

**State**：
```python
class IntentRouteState(TypedDict):
    query: str
    intent: str | None
    response: str | None
```

**路由逻辑**：
- `intent == "gmv"` → `gmv_handler`
- `intent == "order"` → `order_handler`
- 其他 → `common_handler`

```python
def route_intent(state: IntentRouteState) -> Literal["gmv_handler", "order_handler", "common_handler"]:
    intent = state.get("intent", "")
    if intent == "gmv":
        return "gmv_handler"
    elif intent == "order":
        return "order_handler"
    return "common_handler"
```

**任务**：新建 `practice_02_intent_router.py`，测试三个分支都能正确走到。

---

## 练习3：Checkpoint 多轮对话（⭐⭐⭐⭐）
**目标**：掌握 `MemorySaver` + `thread_id` 实现有状态对话

**任务**：新建 `practice_03_multiturn_checkpoint.py`

```python
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()
app = graph.compile(checkpointer=checkpointer)

config = {"configurable": {"thread_id": "user_001"}}

# 第1轮
r1 = app.invoke({
    "query": "近7天GMV",
    "history": [],
    "current_sql": None,
    "result": None
}, config)
print("第1轮:", r1["result"])

# 第2轮（同一个 thread_id，应该能看到历史）
r2 = app.invoke({
    "query": "按区域拆",
    "history": r1.get("history", []),
    "current_sql": r1.get("current_sql"),
    "result": None
}, config)
print("第2轮:", r2["result"])

# 第3轮
r3 = app.invoke({
    "query": "加环比",
    "history": r2.get("history", []),
    "current_sql": r2.get("current_sql"),
    "result": None
}, config)
print("第3轮:", r3["result"])
```

**思考**：多轮对话中，`history` 字段如何自动积累，而不是手动传入？

---

## 练习4：NL2SQL 完整状态机（⭐⭐⭐⭐）
**目标**：综合运用条件边 + 循环 + Checkpoint

**设计的状态机**：

```
START → parse_intent
         ↓
    [intent valid?] → no → fallback → END
         ↓ yes
    generate_sql
         ↓
    [SQL valid?] → no → generate_sql (循环，最多3次)
         ↓ yes
    execute_sql
         ↓
    format_response → END
```

**State**：
```python
class FullNL2SQLState(TypedDict):
    query: str
    intent: str | None
    sql: str | None
    result: str | None
    formatted: str | None
    error: str | None
    attempt: int
    history: list[str]
```

---

## 输出要求

完成后在 `practice_summary.md` 中记录：
1. `__end__` 和 `END` 的区别是什么？
2. Checkpoint 的 `thread_id` 是什么作用？
3. 条件边中返回 `"__end__"` 为什么能让图停止？
