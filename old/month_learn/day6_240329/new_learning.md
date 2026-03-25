# Day6 学习内容：LangChain 全链路综合 & 架构设计

> 🎯 学习目标：建立完整知识体系，理解如何用 LangChain 重构真实项目

---

## 一、LangChain 全景架构

```
┌─────────────────────────────────────────────────────────────┐
│                     LangChain 全栈架构                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    │
│  │   Models    │    │   Memory    │    │     RAG     │    │
│  │   模型层    │    │   记忆层    │    │   知识层    │    │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘    │
│         │                  │                  │            │
│         └──────────────────┼──────────────────┘            │
│                            ↓                               │
│                   ┌─────────────────┐                     │
│                   │      LCEL      │                     │
│                   │   链式编排层    │                     │
│                   └────────┬────────┘                     │
│                            ↓                               │
│                   ┌─────────────────┐                     │
│                   │     Agent       │                     │
│                   │   自主决策层    │                     │
│                   └────────┬────────┘                     │
│                            ↓                               │
│                   ┌─────────────────┐                     │
│                   │    LangServe    │                     │
│                   │    部署层       │                     │
│                   └─────────────────┘                     │
└─────────────────────────────────────────────────────────────┘
```

---

## 二、模块详解

### 2.1 Models（模型层）
LangChain 支持的模型类型：

| 类型 | 说明 | 代表 |
|------|------|------|
| ChatModel | 聊天模型，输入输出都是消息 | ChatOpenAI, ChatAnthropic |
| LLM | 文本模型，输入字符串输出字符串 | OpenAI (text-davinci) |
| Embeddings | 文本向量化 | OpenAIEmbeddings |
| ChatMessage | 消息对象 | HumanMessage, AIMessage, SystemMessage, ToolMessage |

**核心调用方式：**
```python
# 同步
response = llm.invoke("你好")

# 流式（实时看到输出）
for chunk in llm.stream("写一首诗"):
    print(chunk.content, end="")

# 批量（并发处理）
results = llm.batch(["问题1", "问题2", "问题3"])
```

### 2.2 LCEL（LangChain Expression Language）
声明式链接 LangChain 组件的语言。

**为什么需要 LCEL？**
- 统一接口（Runnable 协议）
- 原生流式、异步、并行支持
- 自动日志追踪（LangSmith）
- 无需代码修改即可投入生产

**核心语法：**
```python
# 管道串联
chain = (
    PromptTemplate.from_template("翻译：{text}")
    | llm
    | StrOutputParser()
)

# 调用
result = chain.invoke({"text": "你好"})
```

**Runnable 协议三剑客：**
```python
chain.invoke()   # 同步调用
chain.stream()   # 流式返回
chain.batch()    # 批量处理
```

### 2.3 Memory（记忆层）
让 LLM 记住对话历史。

| 类型 | 策略 | 适合场景 |
|------|------|---------|
| BufferMemory | 存全部 | 短对话 |
| SummaryMemory | 自动摘要 | 长对话 |
| TokenBuffer | 超限截断 | 精确token控制 |
| WindowMemory | 滑动窗口k轮 | 只关心最近N轮 |

**在 LLMChain 中使用：**
```python
memory = ConversationBufferMemory(memory_key="chat_history")

chain = LLMChain(
    llm=llm,
    prompt=PromptTemplate.from_template("{chat_history}\n用户:{input}"),
    memory=memory
)
```

### 2.4 Agent（决策层）
让 LLM 自主决定下一步行动。

**Agent 工作循环：**
```
思考(Thought) → 决策(Action) → 执行 → 观察(Observation) → 循环
```

**Functions Agent 示例：**
```python
from langchain.agents import AgentExecutor, create_openai_functions_agent

agent = create_openai_functions_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
result = agent_executor.invoke({"input": "近7天GMV是多少？"})
```

### 2.5 RAG（检索增强）
让 LLM 基于私域知识库回答问题。

**RAG 流程：**
```
用户问题 → Embedding → 向量检索 → 拼接Context → LLM生成
```

**完整示例：**
```python
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA

# 构建向量数据库
db = FAISS.from_texts(docs, embeddings)
retriever = db.as_retriever(search_kwargs={"k": 2})

# 构建 RAG Chain
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever
)

# 查询
result = qa_chain.invoke({"query": "GMV的口径是什么？"})
```

---

## 三、实战：Codex NL2SQL 重构方案

### 3.1 当前 Java 架构痛点
- LLM 调用逻辑和业务逻辑耦合
- Memory 实现简陋
- 路由是硬编码 if-else
- Prompt 分散难以维护

### 3.2 推荐方案：Java + Python 混合

```
┌─────────────────────────────────────────────────────────────┐
│                     Java 应用（确定性逻辑）                   │
├─────────────────────────────────────────────────────────────┤
│  SQL 编译 │ 权限校验 │ SQL 执行 │ 结果格式化 │ 策略路由   │
└─────────────────────────────┬───────────────────────────────┘
                              │ gRPC / REST
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                 Python 服务（LangChain）                     │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐   │
│  │              LangChain Agent                          │   │
│  │   ├─ Memory（多轮对话记忆）                           │   │
│  │   ├─ Intent Parser（意图解析）                        │   │
│  │   ├─ NL2SQL Chain（LCEL）                           │   │
│  │   └─ RAG（指标定义检索）                             │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 3.3 Python 服务核心实现

```python
"""
NL2SQL Python Service（LangChain 版）
"""
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_functions_agent

class NL2SQLAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model="MiniMax-M2-7", ...)
        self.memory = ConversationBufferMemory(...)
        self.tools = [nl2sql_tool, query_tool]
        self.agent = create_openai_functions_agent(self.llm, self.tools, prompt)
        self.executor = AgentExecutor(agent=self.agent, tools=self.tools, memory=self.memory)
    
    def chat(self, query: str) -> str:
        return self.executor.invoke({"input": query})
```

### 3.4 重构优先级

| 优先级 | 任务 | 说明 |
|--------|------|------|
| P0 | Python 服务骨架 | FastAPI/Flask |
| P0 | Memory 集成 | 多轮对话核心 |
| P0 | Intent Parser | NL2SQL 关键 |
| P1 | RAG 指标检索 | 知识库增强 |
| P2 | LangServe 部署 | 生产就绪 |

---

## 四、组件选择决策树

```
需要调用外部工具？
    │
    ├── 是 → 需要模型自主决策？
    │       ├── 是 → Functions Agent
    │       └── 否 → LLMChain + Tool
    │
    └── 否 → 需要记忆上下文？
            ├── 是 → 需要检索私域知识？
            │       ├── 是 → RAG + Memory
            │       └── 否 → LLMChain + Memory
            └── 否 → 直接调用 LLM
```

---

## 五、知识体系总览

```
                    ┌──────────────────┐
                    │     LangChain     │
                    └────────┬─────────┘
                             │
     ┌───────────┬──────────┼──────────┬───────────┐
     ↓           ↓          ↓          ↓           ↓
  Models       LCEL      Memory      Agent        RAG
  (模型)      (编排)     (记忆)      (决策)      (知识)
     │           │          │          │           │
     ├─invoke    ├─|管道    ├─Buffer   ├─@tool    ├─Embeddings
     ├─stream    ├─Runnable ├─Summary  ├─AgentExe ├─FAISS
     ├─batch     └─Runnable ├─Token    └─Loop     └─RetrievalQA
                             └─Window
```

---

## 六、学习路线总结

### Week 1（已学）✅
- Models / LCEL / Memory / Agent / RAG 基础

### Week 2（进阶）
- LangGraph（状态机编排）
- 复杂 Agent 架构
- LangServe 部署
- LangSmith 监控

### Week 3（精通）
- 生产环境优化
- 性能调优
- 架构设计实战

---

## 七、推荐资源

| 资源 | 地址 |
|------|------|
| LangChain 中文网 | https://www.langchain.com.cn/ |
| LCEL 速查表 | https://www.langchain.com.cn/docs/how_to/lcel_cheatsheet/ |
| 官方英文文档 | https://python.langchain.com/ |
| LangChain Academy | https://academy.langchain.com/ |

---

## 八、学习心得

> 一句话总结 LangChain 的本质：
> 
> **"把 LLM 应用开发的最佳实践封装成可组合的组件，让开发者专注于业务逻辑。"**
