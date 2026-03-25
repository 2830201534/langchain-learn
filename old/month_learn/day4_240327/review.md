# Day4 复习文档：Models + LCEL + Memory 综合

> 📅 复习日期：3月27日（Day1+Day3 内容的二次强化）
> 🎯 复习目标：建立 Models→LCEL→Memory 知识体系

---

## 一、知识架构全景图

```
                    用户输入
                        ↓
┌─────────────────────────────────────────┐
│           PromptTemplate                │
│    (变量注入 / 角色设定 / 消息组织)       │
└──────────────────┬──────────────────────┘
                   ↓
┌─────────────────────────────────────────┐
│     Messages（System/Human/AI/Tool）    │
└──────────────────┬──────────────────────┘
                   ↓
┌─────────────────────────────────────────┐
│        LCEL 链（| 管道串联）             │
│   PromptTemplate | LLM | OutputParser   │
└──────────────────┬──────────────────────┘
                   ↓
┌─────────────────────────────────────────┐
│         Runnable: invoke/stream/batch   │
└──────────────────┬──────────────────────┘
                   ↓
┌─────────────────────────────────────────┐
│              Memory（记忆）              │
│   Buffer / Summary / TokenBuffer / ...  │
└─────────────────────────────────────────┘
```

---

## 二、五种 Memory 对比

| 类型 | 策略 | 优点 | 缺点 | 适合场景 |
|------|------|------|------|---------|
| BufferMemory | 存全部 | 不丢信息 | token爆炸 | <20轮短对话 |
| SummaryMemory | 自动摘要 | token可控 | 损耗/额外开销 | 长对话 |
| TokenBuffer | 超限截断 | 精确控制 | 可能断章 | 精确token控制 |
| WindowMemory | 滑动窗口 | 固定大小 | 历史丢失 | 只关心最近N轮 |
| CombinedMemory | 混合组合 | 灵活 | 配置复杂 | 复杂场景 |

---

## 三、LCEL 核心速记

```python
# 管道串联
chain = A | B | C

# 调用方式
chain.invoke({"x": 1})      # 同步
chain.stream({"x": 1})      # 流式
chain.batch([{"x": 1}])     # 批量

# RunnableLambda
from langchain_core.runnables import RunnableLambda
chain = chain | RunnableLambda(func)
```

---

## 四、LLM 调用三模式

| 模式 | 方法 | 场景 |
|------|------|------|
| 同步 | `invoke()` | 等待完整结果 |
| 流式 | `stream()` | 实时看到输出过程 |
| 批量 | `batch()` | 并发处理多条 |

---

## 五、多轮对话核心原理

```python
# 关键：每轮对话后自动保存到 Memory
chain.invoke({"input": "第1轮问题"})  # → 自动 memory.save_context()
chain.invoke({"input": "第2轮问题"})  # → memory 自动包含第1轮
```

---

## 六、自测问题

1. BufferMemory 和 TokenBufferMemory 的本质区别是什么？

2. 为什么 LCEL 链中 `|` 前面必须是 Runnable 对象？

3. 在 LLMChain 中 Memory 是如何影响 Prompt 的？

4. CombinedMemory 的 `memory_key` 为什么不能重复？

---

## 七、实战要点

**多轮 NL2SQL 的 Memory 配置：**
```python
memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)

chain = LLMChain(
    llm=llm,
    prompt=PromptTemplate.from_template("""
历史：{chat_history}
问题：{input}
表：orders(...)
只输出SQL："""),
    memory=memory  # 关键！
)
```

---

## 八、明日预告

> Day5 新学内容：**Agent + RAG**
- Agent 的"思考 → 决策 → 行动 → 观察"循环
- Functions Agent 的使用方法
- RAG 检索增强的原理和实战
