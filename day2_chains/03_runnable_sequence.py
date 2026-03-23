"""
Day 2 练习 3：RunnableSequence 详解
深入理解 LCEL 的 RunnableSequence 机制
"""

from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.runnable import RunnableSequence

llm = ChatOpenAI(
    model="MiniMax",
    api_key="你的API Key",
    base_url="https://api.minimaxi.com/v1"
)

# 方式1：使用 | 操作符（自动创建 RunnableSequence）
chain1 = PromptTemplate.from_template("解释这个概念：{concept}") | llm | StrOutputParser()

# 方式2：显式创建 RunnableSequence
chain2 = RunnableSequence(
    first=PromptTemplate.from_template("解释这个概念：{concept}"),
    middle=[llm],
    last=StrOutputParser()
)

# 测试两种方式
concept = "LangChain"
print("=== 方式1（| 操作符）===")
print(chain1.invoke({"concept": concept}))

print("\n=== 方式2（显式 RunnableSequence）===")
print(chain2.invoke({"concept": concept}))

# 查看 chain 结构
print("\n=== Chain 结构 ===")
print(chain1)
