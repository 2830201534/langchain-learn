# Day1 练习题：LangGraph 基础

> 🎯 练习目标：掌握 StateGraph / Node / Edge 的基本用法
> ⏰ 预计时间：60 分钟
> 📝 要求：所有代码必须实际运行

---

## 练习1：最小 StateGraph（⭐）
**目标**：跑通 LangGraph 的最基本流程

```python
from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class SimpleState(TypedDict):
    text: str
    count: int

def step1(state: SimpleState) -> SimpleState:
    return {"text": state["text"] + " Hello", "count": state["count"] + 1}

def step2(state: SimpleState) -> SimpleState:
    return {"text": state["text"] + " World", "count": state["count"] + 1}

graph = StateGraph(SimpleState)
graph.add_node("step1", step1)
graph.add_node("step2", step2)
graph.add_edge(START, "step1")
graph.add_edge("step1", "step2")
graph.add_edge("step2", END)

app = graph.compile()
result = app.invoke({"text": "Start", "count": 0})
print(result)
```

**任务**：新建 `practice_01_minimal_graph.py`，运行并打印结果。

---

## 练习2：条件边 - 数字分类（⭐⭐）
**目标**：掌握 `add_conditional_edges` 的用法

**要求**：
1. 创建图：输入数字 → 判断正/负/零 → 输出描述
2. 用条件边实现：正数走"正数处理"，负数走"负数处理"，零走"零处理"

```python
from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class NumberState(TypedDict):
    number: int
    result: str

def process_positive(state: NumberState) -> NumberState:
    return {"result": f"{state['number']} 是正数"}

def process_negative(state: NumberState) -> NumberState:
    return {"result": f"{state['number']} 是负数"}

def process_zero(state: NumberState) -> NumberState:
    return {"result": "输入是零"}

# 条件路由函数
def route(state: NumberState) -> str:
    n = state["number"]
    if n > 0:
        return "positive"
    elif n < 0:
        return "negative"
    else:
        return "zero"

graph = StateGraph(NumberState)
graph.add_node("positive", process_positive)
graph.add_node("negative", process_negative)
graph.add_node("zero", process_zero)
graph.add_edge(START, "route_node")  # 先路由

# ... 关键：如何让 route_node 根据条件走到不同节点？
```

**提示**：
```python
graph.add_conditional_edges(
    "route_node",
    route,
    {
        "positive": "positive",
        "negative": "negative",
        "zero": "zero"
    }
)
```

---

## 练习3：NL2SQL 状态机 - 单轮版（⭐⭐⭐）
**目标**：把 LangChain 的 LCEL Chain 转换为 StateGraph

**任务**：新建 `practice_03_nl2sql_graph.py`，实现：

```
START → parse_intent → generate_sql → execute_sql → format_response → END
```

**State 定义**：
```python
class NL2SQLState(TypedDict):
    query: str              # 用户原始查询
    intent: str | None      # 解析的意图
    sql: str | None         # 生成的SQL
    result: str | None      # 执行结果
    formatted: str | None   # 格式化后的回答
```

**代码模板**：
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from comm.get_pass import get_pass
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END

class NL2SQLState(TypedDict):
    query: str
    intent: str | None
    sql: str | None
    result: str | None
    formatted: str | None

llm = ChatOpenAI(model="MiniMax-M2.7", api_key=get_pass(), base_url="https://api.minimaxi.com/v1")

def parse_intent(state: NL2SQLState) -> NL2SQLState:
    """解析意图"""
    prompt = f"分析查询：{state['query']}\n只输出指标类型（如gmv/order/uv）："
    response = llm.invoke([HumanMessage(content=prompt)])
    intent = response.content.strip()
    return {"intent": intent}

def generate_sql(state: NL2SQLState) -> NL2SQLState:
    """生成SQL"""
    intent = state["intent"]
    if intent == "gmv":
        sql = "SELECT SUM(pay_amount) FROM orders WHERE status='paid' AND created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)"
    elif intent == "order":
        sql = "SELECT COUNT(*) FROM orders WHERE status='paid'"
    else:
        sql = "-- unknown"
    return {"sql": sql}

def execute_sql(state: NL2SQLState) -> NL2SQLState:
    """执行SQL（模拟）"""
    sql = state["sql"]
    if "SUM" in sql:
        return {"result": "¥987,654.32"}
    else:
        return {"result": "12,345"}

def format_response(state: NL2SQLState) -> NL2SQLState:
    """格式化输出"""
    return {"formatted": f"查询结果：{state['result']}"}

# 构建图
graph = StateGraph(NL2SQLState)
graph.add_node("parse_intent", parse_intent)
graph.add_node("generate_sql", generate_sql)
graph.add_node("execute_sql", execute_sql)
graph.add_node("format_response", format_response)
graph.add_edge(START, "parse_intent")
graph.add_edge("parse_intent", "generate_sql")
graph.add_edge("generate_sql", "execute_sql")
graph.add_edge("execute_sql", "format_response")
graph.add_edge("format_response", END)

app = graph.compile()

# 测试
result = app.invoke({"query": "近7天GMV是多少", "intent": None, "sql": None, "result": None, "formatted": None})
print("最终结果：", result["formatted"])
print("生成的SQL：", result["sql"])
```

---

## 练习4：画出你的 NL2SQL 状态机（⭐⭐）
**目标**：理解状态机设计，不写代码

**任务**：在 `practice_04_diagram.md` 中，用 ASCII 图画出你理想中的 NL2SQL 状态机，包括：

- 所有的节点（Node）
- 所有的边（Edge），包括条件边
- 循环路径（如果需要）
- END 终止节点

**思考**：
- 当前 codex 的 RouteDecision 四路路由，在 LangGraph 中如何实现？
- 哪些节点需要循环？（比如 SQL 生成失败重试）
- 哪些节点是并行的？

---

## 输出要求

完成后在 `practice_summary.md` 中记录：
1. `add_edge` 和 `add_conditional_edges` 的区别
2. LangGraph 中的 START 和 END 是什么？
3. State 在整个图中是如何传递的？
