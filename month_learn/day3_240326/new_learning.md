# Day3 学习内容：Memory（对话记忆）

## 一、为什么需要 Memory？
- 问题：LLM 本身没有记忆，每次对话都是全新的
- 解决：把历史对话注入到上下文中
- 场景：多轮对话、"刚才那个指标"等指代词理解

## 二、LangChain Memory 架构

### 2.1 核心接口
- **BaseChatMemory**：所有 Memory 的基类
- **memory_key**：注入到 prompt 的变量名
- **return_messages**：返回 message 对象 vs 字符串

### 2.2 工作原理
```
用户输入 → Memory加载历史 → 拼入Prompt → LLM处理 → 回复保存到Memory
```

### 2.3 在 LCEL 中使用 Memory
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
    memory=memory  # 自动管理历史
)

# 多轮对话
chain.invoke({"input": "我叫张三"})
chain.invoke({"input": "我叫什么名字？"})  # 能记住"张三"
```

## 三、五种 Memory 类型详解

### 3.1 ConversationBufferMemory（全量历史）
- **策略**：保存所有对话历史
- **优点**：信息不丢失，精确还原
- **缺点**：token 消耗大，长对话成本高
```python
from langchain.memory import ConversationBufferMemory

memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)
```

### 3.2 ConversationSummaryMemory（摘要压缩）
- **策略**：对话太长时，用 LLM 生成摘要
- **优点**：token 消耗可控
- **缺点**：有信息损耗，额外 LLM 调用开销
```python
from langchain.memory import ConversationSummaryMemory

memory = ConversationSummaryMemory(llm=llm)  # 需要 LLM 来生成摘要
```

### 3.3 ConversationTokenBufferMemory（Token 限制）
- **策略**：超过 max_token_limit 就截断旧消息
- **优点**：精确控制 token 上限
- **缺点**：可能"断章取义"
```python
from langchain.memory import ConversationTokenBufferMemory

memory = ConversationTokenBufferMemory(
    llm=llm,
    max_token_limit=500  # 超过500token就删旧消息
)
```

### 3.4 ConversationBufferWindowMemory（滑动窗口）
- **策略**：只保留最近 k 轮对话
- **优点**：固定大小，不会无限增长
- **缺点**：早于k轮的上下文完全丢失
```python
from langchain.memory import ConversationBufferWindowMemory

memory = ConversationBufferWindowMemory(k=3)  # 只保留最近3轮
```

### 3.5 CombinedMemory（组合模式）
- **策略**：多种 Memory 组合使用
```python
from langchain.memory import CombinedMemory, ConversationBufferMemory, ConversationSummaryMemory

memory = CombinedMemory(
    memories=[
        ConversationBufferMemory(memory_key="chat_history"),
        ConversationSummaryMemory(llm=llm, memory_key="summary")
    ]
)
```

## 四、Memory 对比速查表

| 类型 | 策略 | 优点 | 缺点 | 适合场景 |
|------|------|------|------|---------|
| BufferMemory | 存全部 | 不丢失信息 | token爆炸 | 短对话(<20轮) |
| SummaryMemory | 自动摘要 | token可控 | 信息损耗 | 长对话 |
| TokenBufferMemory | 超限截断 | 精确控制 | 可能断章 | 精确token控制 |
| BufferWindowMemory | 滑动窗口 | 固定大小 | 历史丢失 | 只关心最近N轮 |
| CombinedMemory | 组合 | 灵活 | 配置复杂 | 复杂场景 |

## 五、实战：多轮 NL2SQL 对话
```python
"""
实战：带 Memory 的多轮 NL2SQL
第1轮：查GMV
第2轮：按区域拆一下
第3轮：还是刚才那个指标，加上环比
"""
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)

chain = LLMChain(
    llm=llm,
    prompt=PromptTemplate.from_template("""历史对话：
{chat_history}

当前问题：{input}
表：orders(id, user_id, pay_amount, status, created_at, region)
status='paid'表示已支付

只输出SQL："""),
    memory=memory,
    verbose=True
)

# 第1轮
result = chain.invoke({"input": "查GMV，近7天的"})
print(result["text"])

# 第2轮（能理解"拆一下"是在GMV基础上的）
result = chain.invoke({"input": "按区域拆一下"})

# 第3轮（关键！能理解"那个指标"指GMV）
result = chain.invoke({"input": "还是刚才那个指标，加上环比数据"})
```

## 六、实战：Memory 在 LCEL 中的正确用法

### 6.1 错误写法
```python
# ❌ Memory 不能直接用在 LCEL 链式表达式中
chain = (
    PromptTemplate.from_template("{input}")
    | llm
    | memory  # 错误！memory 不是 Runnable
)
```

### 6.2 正确写法（使用 LLMChain）
```python
# ✅ 通过 LLMChain 整合 Memory
memory = ConversationBufferMemory(memory_key="history", return_messages=True)

chain = LLMChain(
    llm=llm,
    prompt=PromptTemplate.from_template("{history}\n用户: {input}\nAI:"),
    memory=memory
)
```

### 6.3 在 Agent 中使用 Memory
```python
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.memory import ConversationBufferMemory

memory = ConversationBufferMemory(memory_key="chat_history")

agent = create_openai_functions_agent(llm, tools, prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    memory=memory  # Agent 原生支持 memory
)
```

## 七、与 Java 后端类比（帮助理解）
- **ConversationBufferMemory** ≈ HttpSession（存所有属性）
- **ConversationSummaryMemory** ≈ LRU Cache（自动淘汰旧内容）
- **ConversationTokenBufferMemory** ≈ 固定大小队列（超过就出队）
- **BufferWindowMemory** ≈ 滑动窗口（只关心最近N个）

## 八、学习总结
- Memory 让 LLM "记住"对话历史
- 五种 Memory 各有策略，适合不同场景
- LCEL 中通过 LLMChain 使用 Memory
- Agent 原生支持 memory 参数
- 多轮 NL2SQL 是典型应用场景

## 九、下期预告
- **Day4 新内容**：RAG（检索增强生成）
- **预告**：如何让 AI 基于私域知识库回答问题？
