"""
Day 1 练习 1：基础 API 调用
用 MiniMax API 调用 ChatOpenAI 兼容接口
"""

from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage

# 初始化 LLM（MiniMax 兼容接口）
llm = ChatOpenAI(
    model="MiniMax",
    api_key="你的MiniMax API Key",
    base_url="https://api.minimaxi.com/v1"
)

# 简单调用
response = llm.invoke([HumanMessage(content="你好，请介绍一下自己")])
print("=== 简单调用结果 ===")
print(response.content)
