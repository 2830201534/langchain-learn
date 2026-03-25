# Day1 复习文档：LangChain 核心基础（Models + LCEL）

> 📅 复习日期：3月24日（首次学习后的短期复习）
> 🎯 复习目标：强化记忆，防止遗忘

---

## 一、核心概念速记

### LangChain 是什么？
一个用于开发 LLM 应用的**框架**，简化从开发到生产的全流程。

### LangChain 五大核心库
| 库名 | 作用 |
|------|------|
| `langchain-core` | 基础抽象 + LCEL |
| `langchain` | 链、代理、检索策略 |
| `langchain-community` | 第三方集成 |
| `langgraph` | 有状态多参与者应用 |
| `langserve` | 部署为 REST API |

---

## 二、Models 核心要点

### ChatModel vs LLM
| 对比项 | ChatModel | LLM |
|--------|----------|-----|
| 输入格式 | 消息列表 | 字符串 |
| 输出格式 | ChatMessage | 字符串 |
| 代表 | ChatOpenAI | OpenAI (text-davinci) |

### 模型调用三剑客
```python
# 同步调用
response = llm.invoke("你好")

# 流式调用
for chunk in llm.stream("写一首诗"):
    print(chunk.content, end="")

# 批量调用
results = llm.batch(["问题1", "问题2", "问题3"])
```

### MiniMax 模型配置
```python
llm = ChatOpenAI(
    model="MiniMax-M2.7",
    api_key=get_pass(),
    base_url="https://api.minimaxi.com/v1"
)
```

---

## 三、PromptTemplate 核心要点

### 变量注入
```python
# 单变量
template = PromptTemplate.from_template("翻译：{text}")

# 多变量
template = PromptTemplate.from_template(
    "你是{role}，负责{topic}"
)
```

### ChatPromptTemplate 消息角色
```python
chat_prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个{profession}"),  # 系统角色
    ("human", "{question}")              # 用户问题
])
```

---

## 四、四种 Message 类型

| 类型 | role | 什么时候用 |
|------|------|-----------|
| `HumanMessage` | human | 用户输入 |
| `AIMessage` | ai | AI 回复 |
| `SystemMessage` | system | 设定 AI 角色/规则 |
| `ToolMessage` | tool | 工具执行结果 |

---

## 五、LCEL 核心要点

### 什么是 LCEL？
LangChain Expression Language，用 `|` 管道符串联组件的声明式语法。

### 核心语法
```python
chain = (
    PromptTemplate.from_template("翻译：{text}")
    | llm
    | StrOutputParser()
)
```

### 三个 Runnable 方法
```python
# 流式
chain.stream({"text": "hello"})

# 同步
chain.invoke({"text": "hello"})

# 批量
chain.batch([{"text": "a"}, {"text": "b"}])
```

---

## 六、自测提问

> 尝试回答以下问题，检测掌握程度

1. LangChain 的 `langchain-core` 和 `langchain` 两个库的区别是什么？

2. 为什么需要 `PromptTemplate`？直接写字符串不行吗？

3. `SystemMessage` 和 `HumanMessage` 的本质区别是什么？

4. `|` 管道操作符在 LCEL 中的作用是什么？

5. `invoke()` 和 `stream()` 的使用场景有什么不同？

---

## 七、代码速记

### 最简单的 LCEL 链
```python
chain = (
    PromptTemplate.from_template("翻译成英文：{text}")
    | llm
    | StrOutputParser()
)
result = chain.invoke({"text": "你好"})
```

### 多步串联
```python
step1 = PromptTemplate.from_template("翻译：{x}") | llm | StrOutputParser()
step2 = PromptTemplate.from_template("总结：{x}") | llm | StrOutputParser()
chain = step1 | step2
```

### RunnableLambda 自定义函数
```python
from langchain_core.runnables import RunnableLambda

chain = (
    PromptTemplate.from_template("{text}")
    | llm
    | StrOutputParser()
    | RunnableLambda(lambda x: x.upper())
)
```

---

## 八、记忆卡片

> 遮住答案，检测记忆

**卡片1：**
> Q: LangChain 框架的核心优势是什么？
> A: 简化 LLM 应用生命周期，提供统一的组件接口，支持链式组合

**卡片2：**
> Q: LCEL 的 `|` 管道符本质是什么？
> A: 创建 RunnableSequence，把前一步的输出自动传给下一步输入

**卡片3：**
> Q: 四种 Message 类型的 role 分别是什么？
> A: HumanMessage=human, AIMessage=ai, SystemMessage=system, ToolMessage=tool

---

## 九、实战提示

今晚练习时，重点关注：
- ✅ 模型初始化是否正确（model / api_key / base_url）
- ✅ PromptTemplate 变量名是否拼写一致
- ✅ Message 类型是否用对场景
- ✅ LCEL 链的 `|` 串联顺序是否正确

---

## 十、明日预告

> Day2 新学内容：**Memory（对话记忆）**
- 如何让 AI "记住"对话历史？
- 五种 Memory 类型的区别和选型
- 多轮 NL2SQL 对话实战
