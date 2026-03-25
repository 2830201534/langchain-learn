# Day6 复习文档：一周学习综合总结

> 📅 复习日期：3月29日（本周全部内容的综合复习）
> 🎯 复习目标：建立完整 LangChain 知识体系，能独立构建 LLM 应用

---

## 一、LangChain 学习路径回顾

```
Day1  │ Models + LCEL          │ 基础：如何调用 LLM
Day2  │ 复习强化                │ 巩固核心概念
Day3  │ Memory                 │ 多轮对话记忆
Day4  │ 复习强化                │ Models + Memory 综合
Day5  │ Agent + RAG            │ 自主决策 + 知识检索
Day6  │ 综合总结                │ 架构设计 + 实战
```

---

## 二、核心知识体系

### 2.1 Models（模型层）
```python
# 初始化
llm = ChatOpenAI(
    model="MiniMax-M2.7",
    api_key=get_pass(),
    base_url="https://api.minimaxi.com/v1"
)

# 调用
llm.invoke()     # 同步
llm.stream()     # 流式
llm.batch()      # 批量
```

### 2.2 PromptTemplate（提示词层）
```python
# 字符串模板
template = PromptTemplate.from_template("{var}")

# 消息模板
chat_prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个{role}"),
    ("human", "{input}")
])
```

### 2.3 Messages（消息层）
| 类型 | role | 用途 |
|------|------|------|
| HumanMessage | human | 用户输入 |
| AIMessage | ai | AI回复 |
| SystemMessage | system | 角色设定 |
| ToolMessage | tool | 工具结果 |

### 2.4 LCEL（编排层）
```python
# 管道串联
chain = A | B | C

# Runnable 协议
chain.invoke()   # 同步
chain.stream()   # 流式
chain.batch()    # 批量
```

### 2.5 Memory（记忆层）
| 类型 | 策略 | 场景 |
|------|------|------|
| BufferMemory | 存全部 | 短对话 |
| SummaryMemory | 自动摘要 | 长对话 |
| TokenBuffer | 超限截断 | 精确控制 |
| WindowMemory | 滑动窗口 | 最近N轮 |
| CombinedMemory | 混合 | 复杂场景 |

### 2.6 Agent（决策层）
```
思考(Thought) → 行动(Action) → 观察(Observation) → ... → 回答
```

- `@tool` 定义工具
- `create_openai_functions_agent()` 创建 Agent
- `AgentExecutor` 执行循环

### 2.7 RAG（检索层）
```
用户问题 → Embedding → 向量检索 → 拼接Prompt → LLM生成
```

- `FAISS` 向量数据库
- `RetrievalQA` Chain
- `Embeddings` 向量化

---

## 三、架构设计：Codex 重构方案

### Java + Python 混合架构
```
┌──────────────────────────────────────────────┐
│              Java 应用（确定性逻辑）            │
│  ┌────────────────────────────────────────┐  │
│  │ SQL 编译 │ 权限控制 │ SQL执行 │ 结果格式化 │ │
│  └────────────────────────────────────────┘  │
└────────────────────┬─────────────────────────┘
                     │ gRPC / REST
                     ↓
┌──────────────────────────────────────────────┐
│           Python 服务（LLM 相关）             │
│  ┌────────────────────────────────────────┐  │
│  │ LangChain Agent                        │  │
│  │  ├─ Memory（对话记忆）                  │  │
│  │  ├─ Intent Parser（意图解析）           │  │
│  │  └─ RAG（指标定义检索）                 │  │
│  └────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────┐  │
│  │ NL2SQL Chain（LCEL）                   │  │
│  │  ├─ PromptTemplate                    │  │
│  │  ├─ ChatOpenAI                        │  │
│  │  └─ OutputParser                      │  │
│  └────────────────────────────────────────┘  │
└──────────────────────────────────────────────┘
```

### 迁移优先级
| 优先级 | 任务 | 理由 |
|--------|------|------|
| P0 | Python 服务骨架 | 基础架构 |
| P0 | Memory 集成 | 多轮对话核心 |
| P0 | Intent Parser | NL2SQL 关键 |
| P1 | RAG 指标检索 | 知识库增强 |
| P2 | Agent 决策优化 | 高级能力 |

---

## 四、关键问题解答

### Q1: LCEL 相比普通函数调用的优势？
- 统一接口（Runnable 协议）
- 原生流式、异步支持
- 自动日志追踪
- 并行优化

### Q2: 什么时候用 Memory？用什么类型？
- 短对话（<20轮）→ BufferMemory
- 长对话 → SummaryMemory
- 精确 token 控制 → TokenBufferMemory
- 只关心最近 N 轮 → WindowMemory

### Q3: Agent 和普通 Chain 的区别？
- Chain：固定流程，一步接一步
- Agent：模型自主决策，动态选择下一步

### Q4: RAG 和 Fine-tuning 的选择？
- 知识动态变化 → RAG
- 固定模式/风格 → Fine-tuning

---

## 五、本周学习总结

### 收获
1. _________________________________________________
2. _________________________________________________
3. _________________________________________________

### 困惑
1. _________________________________________________
2. _________________________________________________

### 下一步
1. _________________________________________________
2. _________________________________________________

---

## 六、三周学习路线图

### Week 1（已学）
- ✅ Models / LCEL / Memory / Agent / RAG 基础

### Week 2（进阶）
- LangGraph（状态机编排）
- 复杂 Agent 架构
- 实际项目集成
- LangServe 部署

### Week 3（精通）
- 生产环境优化
- LangSmith 监控
- 性能调优
- 架构设计实战

---

## 七、推荐学习资源

- [LangChain 中文网](https://www.langchain.com.cn/)
- [LCEL 速查表](https://www.langchain.com.cn/docs/how_to/lcel_cheatsheet/)
- [官方英文文档](https://python.langchain.com/)
- LangChain Academy（在线课程）
