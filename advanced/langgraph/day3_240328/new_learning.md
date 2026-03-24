# Day3 · 实战：用 LangGraph 重构 codex 决策链路

## 一、codex 当前 RouteDecision 结构

根据 MEMORY.md 中的记录，codex 当前使用**硬编码的四路路由**：

```
NL2SQL 输入
    ↓
RouteDecision（if-else 判断）
    ├── M4语义查询 → PolicyService → SQL执行
    ├── M2校验引擎
    ├── M7 LLM审查
    └── Fallback
```

问题：
- 每增加一路路由，需要改代码
- 循环重试逻辑散落各处
- 多轮对话的 Memory 独立于路由体系

---

## 二、用 LangGraph 重构后的目标架构

```
                        START
                          ↓
                  ┌── parse_intent ──┐
                  ↓                  ↓
           [intent valid?]      [intent invalid?]
             ↓ yes                  ↓ no
    ┌── route_by_intent ─────────────────→ fallback → END
    ↓
  ┌───────────────────────────────┐
  │  gmv   → gmv_sql_node        │
  │  order → order_sql_node      │
  │  uv    → uv_sql_node         │
  │  other → common_sql_node     │
  └───────────────────────────────┘
                  ↓
         ┌── generate_sql ──┐
         ↓                  ↓
    [SQL valid?]       [SQL invalid?]
      ↓ yes              ↓ no (retry, max=3)
  execute_sql                  ↑
         ↓                     │
    validate_result            │
         ↓                     │
    [result ok?] → no → retry ─┘
         ↓ yes
    format_response → END
```

---

## 三、State 设计

```python
class CodexState(TypedDict):
    """codex LangGraph 状态"""
    # 输入
    query: str                      # 用户原始查询
    thread_id: str                 # 会话ID（用于Checkpoint）

    # 解析层
    intent: str | None             # 解析出的意图
    intent_confidence: float        # 置信度
    parse_error: str | None        # 解析错误

    # SQL生成层
    sql: str | None                # 生成的SQL
    sql_attempt: int               # 当前尝试次数
    max_retries: int               # 最大重试次数

    # 执行层
    result: Any | None             # 执行结果
    execution_error: str | None    # 执行错误

    # 校验层
    validation_result: dict | None # M4校验结果
    policy_result: dict | None     # M7 Policy结果

    # 输出
    response: str | None           # 最终回复
    history: list[str]             # 对话历史（用于Checkpointer）
```

---

## 四、节点实现

### 4.1 parse_intent（解析意图）

```python
def parse_intent(state: CodexState) -> CodexState:
    """解析用户查询，提取意图"""
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import HumanMessage

    llm = ChatOpenAI(model="MiniMax-M2.7", api_key=get_pass(), base_url="https://api.minimaxi.com/v1")

    prompt = f"""分析查询：{state['query']}
表：orders(id, user_id, pay_amount, status, created_at, region)
返回JSON：{{"intent": "gmv|order|uv|other", "confidence": 0.0-1.0}}"""

    response = llm.invoke([HumanMessage(content=prompt)])
    # 解析 JSON ...
    return {"intent": parsed_intent, "intent_confidence": confidence}
```

### 4.2 route_by_intent（意图路由）

```python
from typing import Literal

INTENT_TO_NODE = {
    "gmv": "gmv_sql_node",
    "order": "order_sql_node",
    "uv": "uv_sql_node",
}

def route_by_intent(state: CodexState) -> Literal["gmv_sql_node", "order_sql_node", "uv_sql_node", "common_sql_node", "fallback"]:
    intent = state.get("intent")
    confidence = state.get("intent_confidence", 0)

    if intent in INTENT_TO_NODE and confidence > 0.7:
        return INTENT_TO_NODE[intent]
    return "fallback"
```

### 4.3 SQL 生成节点（以 gmv 为例）

```python
def gmv_sql_node(state: CodexState) -> CodexState:
    """生成 GMV SQL"""
    prompt = f"""为以下查询生成SQL：
Query: {state['query']}
规则：GMV = SUM(pay_amount)，status='paid'
时间：近7天"""

    response = llm.invoke([HumanMessage(content=prompt)])
    return {"sql": sql_text, "sql_attempt": state.get("sql_attempt", 0) + 1}
```

### 4.4 validate_and_execute（校验 + 执行）

```python
def validate_and_execute(state: CodexState) -> CodexState:
    """M4语义校验 + SQL执行"""
    sql = state["sql"]

    # M4 PolicyService 校验
    policy_ok = PolicyService.check(sql)

    # SQL 执行
    if policy_ok:
        result = DB.execute(sql)
        return {"result": result, "validation_result": {"ok": True}}
    return {"validation_result": {"ok": False}, "execution_error": "Policy check failed"}
```

### 4.5 retry_or_end（重试路由）

```python
def retry_or_end(state: CodexState) -> Literal["generate_sql", "__end__"]:
    """根据错误状态决定重试还是结束"""
    has_error = state.get("execution_error") or state.get("validation_result", {}).get("ok") == False
    can_retry = state.get("sql_attempt", 0) < state.get("max_retries", 3)

    if has_error and can_retry:
        return "generate_sql"  # 继续重试
    return "__end__"
```

---

## 五、完整图构建

```python
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()
graph = StateGraph(CodexState)

# 注册所有节点
graph.add_node("parse_intent", parse_intent)
graph.add_node("gmv_sql_node", gmv_sql_node)
graph.add_node("order_sql_node", order_sql_node)
graph.add_node("uv_sql_node", uv_sql_node)
graph.add_node("common_sql_node", common_sql_node)
graph.add_node("fallback", fallback_node)
graph.add_node("validate_and_execute", validate_and_execute)
graph.add_node("format_response", format_response)

# 边
graph.add_edge(START, "parse_intent")

# 条件边：parse → 路由
graph.add_conditional_edges(
    "parse_intent",
    route_by_intent,
    {
        "gmv_sql_node": "gmv_sql_node",
        "order_sql_node": "order_sql_node",
        "uv_sql_node": "uv_sql_node",
        "common_sql_node": "common_sql_node",
        "fallback": "fallback"
    }
)

# SQL生成 → 校验执行
for node in ["gmv_sql_node", "order_sql_node", "uv_sql_node", "common_sql_node"]:
    graph.add_edge(node, "validate_and_execute")

# 条件边：校验结果 → 重试或结束
graph.add_conditional_edges(
    "validate_and_execute",
    retry_or_end,
    {"generate_sql": "gmv_sql_node", "__end__": END}
)

graph.add_edge("fallback", END)
graph.add_edge("format_response", END)

app = graph.compile(checkpointer=checkpointer)
```

---

## 六、重构优势对比

| 维度 | 当前 codex（if-else） | LangGraph 版本 |
|------|---------------------|----------------|
| 新增路由 | 改代码，加 if | 加一个节点函数 + 一行映射 |
| 循环重试 | 散落在各模块 | 集中在条件边 |
| 多轮对话 | 手动管理 Memory | Checkpointer 自动 |
| 调试 | console.log 满天飞 | LangSmith 可视化 trace |
| 可视化 | 无 | 自动生成图结构图 |

---

## 七、重构 Task List（周末执行）

### P0（必须）
- [ ] 将 RouteDecision 的四个分支改为 StateGraph 节点
- [ ] 实现 Checkpointer（多轮对话）
- [ ] 配置 LangSmith（可观测性）

### P1（重要）
- [ ] SQL 重试循环（最多3次）
- [ ] M4 PolicyService 接入
- [ ] M7 LLM 审查节点

### P2（增强）
- [ ] Human-in-the-loop（高风险SQL暂停等确认）
- [ ] 可视化图导出

---

## 八、学习总结

今天完成了：
1. **设计**：codex 目标架构图（State + Node + Edge）
2. **实现**：每个节点的 Python 函数模板
3. **对比**：当前 if-else vs LangGraph 重构的优势
4. **计划**：周末重构的 Task List

---

## 后续路径

LangGraph 掌握后，可以进一步探索：
- **LangGraph 的 Human-in-the-loop**：`interrupt` 节点暂停等人类确认
- **LangSmith**：线上 trace 和调试
- **langgraph.checkpoint.postgres**：生产环境持久化
