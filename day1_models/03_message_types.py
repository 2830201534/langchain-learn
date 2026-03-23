"""
Day 1 练习 3：多种 Message 类型
理解 SystemMessage / HumanMessage / AIMessage 的区别
"""

from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage, AIMessage

llm = ChatOpenAI(
    model="MiniMax",
    api_key="你的MiniMax API Key",
    base_url="https://api.minimaxi.com/v1"
)

# 多消息拼装（带 System Message）
messages = [
    SystemMessage(content="你是一个专业的Python讲师，回答要简洁有趣。"),
    HumanMessage(content="什么是 LangChain？"),
]

response = llm.invoke(messages)
print("=== 多消息调用结果 ===")
print(response.content)

# 对比：没有 SystemMessage 的回答
response2 = llm.invoke([HumanMessage(content="什么是 LangChain？")])
print("\n=== 无 SystemMessage 结果 ===")
print(response2.content)
