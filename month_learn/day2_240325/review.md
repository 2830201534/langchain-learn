# Day2 复习文档：LangChain 核心基础（综合）

> 📅 复习日期：3月25日（Day1 内容的首次强化复习）
> 🎯 复习目标：巩固 Day1 所学，建立知识关联

---

## 一、LangChain 核心架构

```
┌─────────────────────────────────────────────────────┐
│                    LangChain 框架                     │
├─────────────────────────────────────────────────────┤
│  langchain-core  │ 基础抽象 + LCEL表达式语言           │
│  langchain       │ 链、代理、检索策略（认知架构）       │
│  langchain-community │ 第三方集成                      │
│  langgraph       │ 有状态多参与者应用                  │
│  langserve       │ REST API 部署                      │
└─────────────────────────────────────────────────────┘
```

---

## 二、四种 Message 对比

| 类型 | role | 输入/输出 | 典型场景 |
|------|------|---------|---------|
| HumanMessage | human | 输入 | 用户提问 |
| AIMessage | ai | 输出 | 模型回复 |
| SystemMessage | system | 配置 | 设定角色/规则 |
| ToolMessage | tool | 中间 | 工具返回结果 |

---

## 三、LCEL 三大特性

### 1. 流式支持（Streaming）
```python
# 流式：实时看到输出
for chunk in chain.stream({"input": "写一首诗"}):
    print(chunk, end="", flush=True)
```

### 2. 异步支持（Async）
```python
# 异步：高效处理并发请求
result = await chain.ainvoke({"input": "hello"})
```

### 3. 并行执行（Parallel）
```python
# batch：批量处理
results = chain.batch([
    {"input": "问题1"},
    {"input": "问题2"},
    {"input": "问题3"}
])
```

---

## 四、Runnable 协议三剑客

| 方法 | 作用 | 返回类型 |
|------|------|---------|
| `invoke()` | 同步调用 | 最终结果 |
| `stream()` | 流式返回 | 发生器 |
| `batch()` | 批量调用 | 结果列表 |

---

## 五、PromptTemplate vs ChatPromptTemplate

```python
# PromptTemplate：简单字符串模板
template = PromptTemplate.from_template("翻译：{text}")

# ChatPromptTemplate：消息角色模板
chat_prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个{role}"),
    ("human", "{question}")
])
```

---

## 六、关键问题自测

### Q1: 为什么 LCEL 用 `|` 管道符？
因为 `|` 会创建 `RunnableSequence`，自动把前一步的输出传给下一步输入。

### Q2: SystemMessage 和普通 HumanMessage 的区别？
SystemMessage 设置 AI 的"角色设定"，不影响对话流程；HumanMessage 是用户实际输入。

### Q3: `invoke()` 和 `stream()` 的本质区别？
- `invoke()`：等全部计算完成，返回完整结果
- `stream()`：边计算边返回，像"打字机"一样逐步输出

---

## 七、代码速记卡

**初始化 MiniMax 模型：**
```python
llm = ChatOpenAI(
    model="MiniMax-M2.7",
    api_key=get_pass(),
    base_url="https://api.minimaxi.com/v1"
)
```

**最简单的 LCEL 链：**
```python
chain = (
    PromptTemplate.from_template("翻译：{text}")
    | llm
    | StrOutputParser()
)
```

**多步串联：**
```python
chain = step1 | step2 | step3
```

---

## 八、知识关联图

```
Models（模型）
    ↓
    ├─ ChatModel / LLM
    ├─ invoke() / stream() / batch()
    └─ API Key / Base URL 配置

PromptTemplate（提示词模板）
    ↓
    ├─ from_template() 方式
    ├─ 变量注入 {var_name}
    └─ ChatPromptTemplate（多角色）

Messages（消息类型）
    ↓
    ├─ HumanMessage → 用户输入
    ├─ AIMessage → AI回复
    ├─ SystemMessage → 角色设定
    └─ ToolMessage → 工具结果

LCEL（表达式语言）
    ↓
    ├─ | 管道符串联
    ├─ Runnable 协议
    └─ invoke / stream / batch
```

---

## 九、今天的状态检查

在练习文件 `practice_summary.md` 中记录：

- [ ] 练习1~8 是否全部完成？
- [ ] 哪个练习遇到困难？
- [ ] 对 LCEL 的理解程度（1~5分）？
- [ ] 明天想深入研究哪个方向？

---

## 十、今日总结

> 用 3 句话总结今天的收获：
>
> 1. _________________________________________________
> 2. _________________________________________________
> 3. _________________________________________________
