"""
Day 1 练习 2：PromptTemplate 动态拼装
学会用 PromptTemplate 注入变量
"""

import sys
from pathlib import Path

from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import HumanMessage

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from comm.get_pass import get_pass

llm = ChatOpenAI(
    model="MiniMax-M2.7",
    api_key=get_pass(),
    base_url="https://api.minimaxi.com/v1"
)

# 简单变量注入
template = PromptTemplate.from_template("请把以下中文翻译成英文：{text}")
prompt = template.invoke({"text": " LangChain 真好玩！"})

response = llm.invoke([HumanMessage(content=prompt.text)])
print("=== 变量注入结果 ===")
print(response.content)
