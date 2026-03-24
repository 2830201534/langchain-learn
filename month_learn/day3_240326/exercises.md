# Day3 练习题：Memory（对话记忆）

> 🎯 练习目标：掌握五种 Memory 类型，理解多轮对话原理
> ⏰ 预计时间：45~60 分钟
> 📝 要求：所有代码必须实际运行

---

## 练习1：ConversationBufferMemory 基础（⭐）
**目标**：掌握最基本的 Memory 用法

```python
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)

chain = LLMChain(
    llm=llm,
    prompt=PromptTemplate.from_template("{chat_history}\n用户: {input}\nAI:"),
    memory=memory
)

# 多轮对话
chain.invoke({"input": "我叫张三"})
chain.invoke({"input": "我叫什么名字？"})  # 应该记住"张三"
```

**任务**：
1. 新建文件 `practice_01_buffer_memory.py`
2. 实现 3 轮以上对话
3. 打印 `memory.chat_memory.messages` 查看存储结构

---

## 练习2：对比三种 Memory（⭐⭐）
**目标**：理解 Buffer / Summary / TokenBuffer 的差异

**任务**：
1. 新建文件 `practice_02_memory_compare.py`
2. 分别创建三种 Memory 实例
3. 模拟同一个 10 轮对话场景
4. 对比：
   - BufferMemory：存了多少条消息？
   - SummaryMemory：生成了什么摘要？
   - TokenBufferMemory（max_token_limit=200）：超过后如何处理？

---

## 练习3：带 Memory 的 NL2SQL（⭐⭐⭐）
**目标**：掌握 Memory 在实际场景中的应用

**任务**：
1. 新建文件 `practice_03_nl2sql_memory.py`
2. 实现多轮 NL2SQL 对话：

```
第1轮：用户 → "查近7天GMV"
        AI → SQL: SELECT SUM(pay_amount)...

第2轮：用户 → "按区域拆一下"（应理解在GMV基础上加分组）
        AI → SQL: SELECT SUM(pay_amount), region...

第3轮：用户 → "还是刚才那个指标，加上环比"
        AI → SQL: 应理解"那个指标"=GMV，加环比计算
```

**提示**：
```python
chain = LLMChain(
    llm=llm,
    prompt=PromptTemplate.from_template("""历史对话：
{chat_history}

当前问题：{input}
表：orders(id, user_id, pay_amount, status, created_at, region)
status='paid'表示已支付

要求：理解"那个指标"等指代词
只输出SQL："""),
    memory=memory
)
```

---

## 练习4：ConversationBufferWindowMemory 滑动窗口（⭐⭐⭐）
**目标**：理解"只关心最近N轮"的 Memory 策略

**任务**：
1. 新建文件 `practice_04_window_memory.py`
2. 设置 `k=2`（只保留最近2轮）
3. 进行 5 轮对话
4. 观察：第1轮对话是否还在 Memory 中？

---

## 练习5：CombinedMemory 组合使用（⭐⭐⭐⭐）
**目标**：掌握多种 Memory 组合的用法

**任务**：
1. 新建文件 `practice_05_combined_memory.py`
2. 组合 BufferMemory + SummaryMemory
3. 验证两者是否同时生效

```python
from langchain.memory import CombinedMemory, ConversationBufferMemory, ConversationSummaryMemory

memory = CombinedMemory(
    memories=[
        ConversationBufferMemory(memory_key="chat_history"),
        ConversationSummaryMemory(llm=llm, memory_key="summary")
    ]
)
```

---

## 练习6：Memory 与 Agent 整合（⭐⭐⭐⭐）
**目标**：掌握 Agent 中使用 Memory 的方式

**任务**：
1. 新建文件 `practice_06_agent_memory.py`
2. 构建带 Memory 的 Functions Agent
3. 实现多轮工具调用对话

```python
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    memory=memory  # 只需传入 memory 参数
)
```

---

## 练习7：挑战题 - Memory 状态持久化（⭐⭐⭐⭐⭐）
**目标**：理解 Memory 状态如何持久化到外部存储

**任务**：
1. 新建文件 `practice_07_memory_persist.py`
2. 将 Memory 的聊天记录保存到 JSON 文件
3. 重新加载 Memory 时能恢复历史对话

```python
import json
from pathlib import Path

# 保存
def save_memory(memory, filepath):
    messages = memory.chat_memory.messages
    data = [{"type": m.type, "content": m.content} for m in messages]
    Path(filepath).write_text(json.dumps(data, ensure_ascii=False))

# 加载
def load_memory(memory, filepath):
    data = json.loads(Path(filepath).read_text())
    from langchain_core.messages import HumanMessage, AIMessage
    for msg in data:
        memory.chat_memory.add_message(
            HumanMessage(content=msg["content"]) if msg["type"] == "human" 
            else AIMessage(content=msg["content"])
        )
```

---

## 输出要求

完成后在 `practice_summary.md` 中记录：
1. 每个练习的关键发现
2. 三种 Memory 的使用场景总结
3. Memory 持久化的实现思路
