# ---encoding:utf-8---
# @Time    : 2026/3/25 13:46
# @Author  : HeJie
# @Email   ：hejie@terminus.io
# @File    : 1.run_demo.py
# @Project : langchain-learn工具开发


import os

from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate


api_key = os.getenv("MINIMAX_API_KEY")
api_host = os.getenv("MINIMAX_API_HOST")

prompt = ChatPromptTemplate.from_messages(
    [("human", "我是{name}，来自{unv}，你了解吗")]
)

llm = ChatOpenAI(
    model="MiniMax-M2.7",
    api_key=api_key,
    base_url=api_host
)

chain = prompt | llm | StrOutputParser()

result = chain.invoke({"name":"皮蛋", "unv":"吉首大学"})

print(result)