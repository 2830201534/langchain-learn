# Day6 练习题：LangChain 完整项目演练 + 架构设计

> 🎯 练习目标：用 LangChain 从头实现 NL2SQL 核心流程，完成架构设计
> ⏰ 预计时间：90 分钟
> 📝 要求：所有代码必须实际运行，有问题随时 debug

---

## 练习1：最小化 NL2SQL Chain（⭐⭐⭐）
**目标**：用 LCEL 实现"自然语言 → SQL"的单轮查询

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from comm.get_pass import get_pass
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from pydantic import BaseModel

llm = ChatOpenAI(
    model="MiniMax-M2.7",
    api_key=get_pass(),
    base_url="https://api.minimaxi.com/v1"
)

# 定义意图解析输出格式
class NL2SQLIntent(BaseModel):
    metric: str
    aggregation: str
    time_range: str
    filters: list[str]

from langchain_core.output_parsers import JsonOutputParser

prompt = PromptTemplate.from_template("""分析查询，提取指标信息。
表：orders(id, user_id, pay_amount, status, created_at, region)
规则：status='paid' 表示已支付

查询：{query}

输出JSON格式：
- metric: 指标名（如gmv/order/uv）
- aggregation: 聚合方式（如SUM/COUNT/AVG）
- time_range: 时间范围（如近7天）
- filters: 过滤条件列表
""")

chain = (
    prompt
    | llm
    | JsonOutputParser(pydantic_model=NL2SQLIntent)
)

result = chain.invoke({"query": "近7天GMV是多少"})
print(result)
```

**任务**：新建 `practice_01_nl2sql_basic.py`：
1. 运行上面的代码，看意图解析结果
2. 把意图解析的结果拼接成 SQL（规则：GMV=SUM(pay_amount)，order=COUNT(id)，UV=COUNT(DISTINCT user_id)）
3. 测试："近30天订单数"、"UV是多少"

---

## 练习2：带 Memory 的多轮 NL2SQL（⭐⭐⭐⭐）
**目标**：让 NL2SQL 支持多轮对话，理解上下文

**任务**：新建 `practice_02_multiturn_nl2sql.py`：

```python
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)

prompt = PromptTemplate.from_template("""历史对话：
{chat_history}

当前问题：{input}
表：orders(id, user_id, pay_amount, status, created_at, region)
status='paid'表示已支付

要求：
1. 理解"刚才那个指标"等指代词
2. 只输出SQL，不要解释

SQL：""")

chain = LLMChain(llm=llm, prompt=prompt, memory=memory)

# 第1轮
r1 = chain.invoke({"input": "近7天GMV是多少"})
print("第1轮 SQL:", r1["text"])

# 第2轮（应该理解是在GMV基础上"按区域拆一下"）
r2 = chain.invoke({"input": "按区域拆一下"})
print("第2轮 SQL:", r2["text"])

# 第3轮（应该理解"那个指标"=GMV）
r3 = chain.invoke({"input": "还是刚才那个指标，加上环比"})
print("第3轮 SQL:", r3["text"])
```

**验收标准**：
- 第2轮 SQL 中有 `GROUP BY region`
- 第3轮 SQL 中有 GMV 的 SUM + 环比计算

---

## 练习3：完整 NL2SQL Pipeline（⭐⭐⭐⭐⭐）
**目标**：实现完整的 NL2SQL Chain：意图解析 → SQL生成 → 执行 → 格式化回答

**任务**：新建 `practice_03_full_pipeline.py`：

```python
"""
完整 NL2SQL Pipeline：

用户问题
    ↓
parse_intent() → {metric, aggregation, time_range, filters}
    ↓
build_sql() → SQL字符串（规则引擎，非LLM生成）
    ↓
execute_sql() → 执行结果（这里用模拟数据）
    ↓
format_response() → 自然语言回答
"""

from typing import TypedDict

class NL2SQLState(TypedDict):
    query: str
    intent: dict | None
    sql: str | None
    result: str | None
    response: str | None

def parse_intent(state: NL2SQLState) -> NL2SQLState:
    """解析意图（用 LLM）"""
    from langchain_openai import ChatOpenAI
    from langchain_core.output_parsers import JsonOutputParser
    from langchain_core.prompts import PromptTemplate
    from pydantic import BaseModel

    class Intent(BaseModel):
        metric: str
        aggregation: str
        time_range: str

    llm = ChatOpenAI(model="MiniMax-M2.7", api_key=get_pass(), base_url="https://api.minimaxi.com/v1")

    prompt = PromptTemplate.from_template("分析查询：{query}\n表：orders\n输出JSON：")
    chain = prompt | llm | JsonOutputParser(pydantic_model=Intent)

    result = chain.invoke({"query": state["query"]})
    return {"intent": result}

def build_sql(state: NL2SQLState) -> NL2SQLState:
    """根据意图构建 SQL（确定性规则，非生成）"""
    metric_map = {
        "gmv": "SUM(pay_amount)",
        "order": "COUNT(id)",
        "uv": "COUNT(DISTINCT user_id)"
    }
    intent = state["intent"]
    metric = intent.get("metric", "gmv").lower()
    agg = metric_map.get(metric, "COUNT(*)")

    sql = f"SELECT {agg} FROM orders WHERE status='paid'"
    return {"sql": sql}

def execute_sql(state: NL2SQLState) -> NL2SQLState:
    """模拟执行"""
    sql = state["sql"]
    if "SUM" in sql:
        return {"result": "¥987,654.32"}
    elif "COUNT(DISTINCT" in sql:
        return {"result": "12,345"}
    else:
        return {"result": "99,999"}

def format_response(state: NL2SQLState) -> NL2SQLState:
    """格式化自然语言回答"""
    intent = state["intent"]
    result = state["result"]
    metric = intent.get("metric", "GMV").upper() if intent else "GMV"
    return {"response": f"{metric}查询结果：{result}"}

# 串联成 Chain（用 LCEL）
from langchain_core.runnables import RunnableLambda

chain = (
    RunnableLambda(parse_intent)
    | RunnableLambda(build_sql)
    | RunnableLambda(execute_sql)
    | RunnableLambda(format_response)
)

result = chain.invoke({"query": "近7天GMV是多少"})
print("最终回答：", result["response"])
print("生成的SQL：", result["sql"])
```

---

## 练习4：Python vs Java 架构对比（⭐⭐⭐）
**目标**：理解 Python 原型和 Java 生产环境的架构差异

**任务**：在 `practice_04_architecture.md` 中画出两种架构图：

### 4.1 Python 原型架构（LCEL）
```
用户查询 → Memory → Intent Parser(LLM) → SQL Generator(规则) → 执行 → 格式化
```

### 4.2 Java 生产架构（codex 现状）
```
用户查询 → RouteDecision(if-else) → [M4语义查询|M2校验|M7审查] → SQL执行 → 返回
```

### 4.3 思考并记录：
- Python 原型的优势/劣势？
- Java 架构的问题点？（RouteDecision 硬编码、Memory 缺失）
- 改进方案？（用 LangGraph 重构 RouteDecision）

---

## 练习5：LangGraph 重构 RouteDecision 草图（⭐⭐⭐⭐）
**目标**：用 LangGraph 的思路重新设计 codex 的决策链路

**任务**：新建 `practice_05_langgraph_redesign.py`：

```python
"""
用 LangGraph 重构 codex RouteDecision 的思路：

class CodexState(TypedDict):
    query: str
    intent: str | None
    sql: str | None
    result: str | None

# 节点
def parse_intent(state: CodexState) -> CodexState:
    # 调用 LLM 解析意图
    pass

def route_by_intent(state: CodexState) -> str:
    # 条件边路由
    if state["intent"] == "gmv":
        return "gmv_sql_node"
    elif state["intent"] == "order":
        return "order_sql_node"
    return "fallback"

# ... 其他节点
```

**产出**：在文件底部画 ASCII 图，表示重构后的状态机

---

## 输出要求

完成后在 `practice_summary.md` 中记录：
1. 规则引擎生成 SQL vs LLM 生成 SQL 的优劣对比
2. Python 原型中 Memory 的实现方式
3. LangGraph 重构 codex 的核心价值点
