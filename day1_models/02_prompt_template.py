"""
Day 1 练习 2：PromptTemplate 动态拼装
学会用 PromptTemplate 注入变量
"""

from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage

llm = ChatOpenAI(
    model="MiniMax",
    api_key="你的MiniMax API Key",
    base_url="https://api.minimaxi.com/v1"
)

# 简单变量注入
template = PromptTemplate.from_template("请把以下中文翻译成英文：{text}")
prompt = template.invoke({"text": " LangChain 真好玩！"})

response = llm.invoke([HumanMessage(content=prompt.text)])
print("=== 变量注入结果 ===")
print(response.content)
