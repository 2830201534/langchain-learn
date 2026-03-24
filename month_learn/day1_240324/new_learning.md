# Day1 学习内容：LangChain 核心基础（Models + LCEL）

## 一、LangChain 是什么？
- 解释 LangChain 框架的定义和作用
- LangChain 解决了什么问题
- 核心价值：简化 LLM 应用生命周期（开发→生产化→部署）

## 二、LangChain 架构（5个核心库）
- langchain-core：基础抽象和 LCEL
- langchain-community：第三方集成
- langchain：链、代理、检索策略（认知架构）
- langgraph：多参与者有状态应用程序
- langserve：部署为 REST API
- langsmith：调试、测试、评估、监控

## 三、Models（模型）— 从零讲解
### 3.1 什么是 ChatModel / LLM？
- ChatModel vs LLM 的区别
- 输入输出格式差异

### 3.2 如何初始化模型
- 以 MiniMax 为例（兼容 OpenAI 接口）
- 关键参数：model, api_key, base_url

### 3.3 调用方式
- invoke()：同步调用
- stream()：流式返回
- batch()：批量调用

### 3.4 代码示例
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from comm.get_pass import get_pass
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="MiniMax-M2.7",
    api_key=get_pass(),
    base_url="https://api.minimaxi.com/v1"
)

# 同步调用
response = llm.invoke("你好，请介绍一下自己")
print(response.content)

# 流式调用
for chunk in llm.stream("写一首关于AI的小诗"):
    print(chunk.content, end="", flush=True)
```

## 四、PromptTemplate（提示词模板）— 从零讲解
### 4.1 什么是 PromptTemplate？
- 为什么需要模板：变量注入、复用

### 4.2 PromptTemplate 的用法
- from_template() 方式
- input_variables 参数

### 4.3 代码示例
```python
from langchain_core.prompts import PromptTemplate

# 简单变量注入
template = PromptTemplate.from_template("请把以下中文翻译成英文：{text}")
prompt = template.invoke({"text": "LangChain真强大"})

# 多变量模板
multi_template = PromptTemplate.from_template(
    "你是{role}，负责{topic}。用户说：{user_input}"
)
prompt = multi_template.invoke({
    "role": "翻译助手",
    "topic": "中英互译",
    "user_input": "今天天气真好"
})
```

### 4.4 ChatPromptTemplate（聊天场景）
```python
from langchain_core.prompts import ChatPromptTemplate

chat_prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个专业的{profession}。"),
    ("human", "用户问题：{question}")
])

result = chat_prompt.invoke({
    "profession": "Python讲师",
    "question": "什么是生成器？"
})
```

## 五、Messages（消息类型）— 从零讲解
### 5.1 四种核心消息类型

| 类型 | role | 说明 | 典型场景 |
|------|------|------|---------|
| HumanMessage | human | 用户消息 | 用户提问 |
| AIMessage | ai | AI回复 | 模型输出 |
| SystemMessage | system | 系统指令 | 设定角色 |
| ToolMessage | tool | 工具结果 | 函数返回 |

### 5.2 代码示例
```python
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage

# 人类消息
human_msg = HumanMessage(content="今天天气怎么样？")

# AI消息
ai_msg = AIMessage(content="今天是晴天，温度20度。")

# 系统消息（设定AI角色）
system_msg = SystemMessage(content="你是一个严谨的数据分析师。")

# 工具消息（工具执行结果）
tool_msg = ToolMessage(
    content='{"temperature": 20}',
    tool_call_id="abc123",  # 关联tool_call_id
    name="get_weather"
)
```

### 5.3 多消息组合
```python
messages = [
    SystemMessage(content="你是一个专业的翻译助手。"),
    HumanMessage(content="把下面的中文翻译成英文：{text}"),
]

response = llm.invoke(messages)
```

## 六、LCEL（LangChain Expression Language）— 核心重点
### 6.1 什么是 LCEL？
- LangChain Expression Language
- 声明式链接 LangChain 组件的方式
- 核心语法：用 `|` 管道符串联

### 6.2 为什么需要 LCEL？
- 统一接口（Runnable 协议）
- 原生支持流式、异步、并发
- 自动日志追踪（LangSmith）
- 无需代码修改即可投入生产

### 6.3 快速上手：`|` 管道操作符
```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

llm = ChatOpenAI(model="MiniMax-M2.7", api_key=get_pass(), base_url="https://api.minimaxi.com/v1")

# 最简单的 LCEL 链：Prompt → LLM → OutputParser
chain = (
    PromptTemplate.from_template("把以下中文翻译成英文：{text}")
    | llm
    | StrOutputParser()
)

# 调用
result = chain.invoke({"text": "LangChain真强大"})
print(result)  # 直接输出纯文本
```

### 6.4 LCEL 的优势（6个关键点）
1. **一流流式支持**：首次 token 时间最优
2. **异步支持**：同步/异步用同一套 API
3. **并行执行**：多个步骤自动并发
4. **重试和回退**：链的任意部分可配置
5. **访问中间结果**：可获取中间步骤输出
6. **输入输出模式**：Pydantic / JSONSchema 验证

### 6.5 多步串联示例
```python
# Step 1: 中文 → 英文
step1 = PromptTemplate.from_template("翻译成英文：{text}") | llm | StrOutputParser()

# Step 2: 英文 → 中文（意译）
step2 = PromptTemplate.from_template("用更优雅的方式表达：{text}") | llm | StrOutputParser()

# Step 3: 总结
step3 = PromptTemplate.from_template("用一句话总结：{text}") | llm | StrOutputParser()

# 串联三步
chain = step1 | step2 | step3

result = chain.invoke({"text": "今天天气真好"})
```

### 6.6 Runnable 协议（三个核心方法）
```python
# stream: 流式返回
for chunk in chain.stream({"text": "hello"}):
    print(chunk)

# invoke: 同步调用
result = chain.invoke({"text": "hello"})

# batch: 批量调用
results = chain.batch([{"text": "hello"}, {"text": "world"}])
```

### 6.7 自定义函数接入 LCEL
```python
from langchain_core.runnables import RunnableLambda

# 普通函数 → LCEL 可运行单元
def add_exclamation(text):
    return text + "!"

chain = (
    PromptTemplate.from_template("说{text}")
    | llm
    | StrOutputParser()
    | RunnableLambda(add_exclamation)
)
```

## 七、综合实战：构建一个 NL2SQL 查询链
```python
"""
实战：构建一个 NL2SQL 查询链
用户输入自然语言 → LLM解析意图 → 生成SQL
"""
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import Optional

llm = ChatOpenAI(model="MiniMax-M2.7", api_key=get_pass(), base_url="https://api.minimaxi.com/v1")

# 定义输出结构
class NL2SQLIntent(BaseModel):
    metric: str = Field(description="指标名称，如 GMV、订单数")
    aggregation: str = Field(description="聚合方式，如 SUM、COUNT")
    time_range: str = Field(description="时间范围，如 近7天")

# 意图解析链
intent_chain = (
    PromptTemplate.from_template("""分析查询，提取信息。
查询：{query}
表结构：orders(id, user_id, pay_amount, status, created_at)
输出JSON：""")
    | llm
    | JsonOutputParser(pydantic_model=NL2SQLIntent)
)

# SQL生成链
sql_chain = (
    PromptTemplate.from_template("""根据意图生成SQL。
意图：{intent}
表：orders(status='paid'表示已支付)
只输出SQL：""")
    | llm
    | StrOutputParser()
)

# 完整链
nl2sql_chain = intent_chain | sql_chain

# 测试
result = nl2sql_chain.invoke({"query": "近7天GMV是多少"})
print(result)
```

## 八、学习总结 & 关键点回顾
- LangChain 5个核心库的作用
- ChatModel vs LLM 的区别
- PromptTemplate / ChatPromptTemplate 用法
- 四种 Message 类型及区别
- LCEL 核心语法 `|` 管道串联
- Runnable 三剑客：invoke / stream / batch

## 九、下期预告
- Day2 新内容：Memory 对话记忆机制
- 预告：如何让 AI "记住"对话历史？
