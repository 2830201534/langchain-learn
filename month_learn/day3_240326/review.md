# Day3 复习文档：Memory（对话记忆）

> 📅 复习日期：3月26日（Day1+Day3 内容的强化复习）
> 🎯 复习目标：掌握 Memory 机制，理解多轮对话原理

---

## 一、为什么需要 Memory？

LLM 本身是**无状态的**——每次调用都是独立的，历史对话需要手动注入。

```
无状态：用户:你好 → AI:你好 → 用户:我叫什么？→ AI:不知道
有记忆：用户:我叫张三 → AI:你好张三 → 用户:我叫什么？→ AI:你叫张三
```

---

## 二、五种 Memory 对比

| 类型 | 策略 | 优点 | 缺点 | 适合场景 |
|------|------|------|------|---------|
| `ConversationBufferMemory` | 存全部 | 不丢信息 | token爆炸 | <20轮短对话 |
| `ConversationSummaryMemory` | 自动摘要 | token可控 | 有损耗 | 长对话 |
| `ConversationTokenBufferMemory` | 超限截断 | 精确控制 | 可能断章 | 精确token |
| `ConversationBufferWindowMemory` | 滑动窗口k轮 | 固定大小 | 历史丢失 | 只关心最近 |
| `CombinedMemory` | 混合组合 | 灵活 | 配置复杂 | 特殊场景 |

---

## 三、Memory 核心用法

### BufferMemory
```python
memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)
```

### SummaryMemory
```python
memory = ConversationSummaryMemory(llm=llm)
```

### TokenBufferMemory
```python
memory = ConversationTokenBufferMemory(
    llm=llm,
    max_token_limit=500
)
```

### WindowMemory
```python
memory = ConversationBufferWindowMemory(k=3)
```

---

## 四、在 LLMChain 中使用 Memory

```python
chain = LLMChain(
    llm=llm,
    prompt=PromptTemplate.from_template("{chat_history}\n用户: {input}\nAI:"),
    memory=memory  # 关键！
)
```

---

## 五、多轮 NL2SQL 场景

```
第1轮：查GMV，近7天
       → SQL: SELECT SUM(pay_amount) WHERE status='paid' AND created_at >= ...

第2轮：按区域拆一下
       → SQL: SELECT SUM(pay_amount), region WHERE ... GROUP BY region

第3轮：还是刚才那个指标，加上环比
       → 关键！"那个指标"指GMV，"刚才"指近7天
       → SQL: SELECT SUM(pay_amount), SUM(pay_amount)/LAG(...) ...
```

**Memory 如何帮助：**
- 第1轮后：memory 保存了"查GMV，近7天"
- 第2轮后：memory 保存了"按区域拆一下"和对应SQL
- 第3轮：memory 包含前两轮，LLM 能理解"那个指标"

---

## 六、与 Java 类比

| LangChain | Java | 说明 |
|-----------|------|------|
| BufferMemory | HttpSession | 存所有属性 |
| SummaryMemory | LRU Cache | 自动淘汰旧内容 |
| TokenBufferMemory | 固定大小Queue | 超过就出队 |
| WindowMemory | 滑动窗口 | 只关心最近N个 |

---

## 七、自测问题

1. 为什么 LLM 本身没有"记忆"？
2. BufferMemory 的 token 爆炸问题怎么解决？
3. SummaryMemory 的"摘要"是谁生成的？
4. CombinedMemory 的两个 memory_key 可以相同吗？

---

## 八、知识关联

```
用户输入
    ↓
Memory.load_memory_variables() → 加载历史
    ↓
PromptTemplate（拼入历史）
    ↓
LLM 处理
    ↓
Memory.save_context() → 保存本轮
```

---

## 九、明日预告

> Day5 新学内容：**Agent + RAG**
- Agent 如何"自主决策"
- RAG 检索增强的原理
