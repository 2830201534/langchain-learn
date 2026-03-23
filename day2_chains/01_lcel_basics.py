"""
Day 2 练习 1：LCEL 基础管道
使用 | 管道操作符串接 Prompt → LLM → OutputParser
"""

from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema import StrOutputParser

llm = ChatOpenAI(
    model="MiniMax",
    api_key="你的API Key",
    base_url="https://api.minimaxi.com/v1"
)

# 构建翻译 Chain
chain = (
    PromptTemplate.from_template("把以下中文翻译成英文：{text}")
    | llm
    | StrOutputParser()
)

# invoke 方式调用
result = chain.invoke({"text": "近7天 GMV 是多少"})
print("=== LCEL invoke 结果 ===")
print(result)

# stream 方式调用（流式输出）
print("\n=== LCEL stream 结果 ===")
for chunk in chain.stream({"text": "LangChain 真强大"}):
    print(chunk, end="", flush=True)
print()
