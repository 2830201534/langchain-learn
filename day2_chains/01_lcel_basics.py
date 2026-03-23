"""
Day 2 练习 1：LCEL 基础管道
使用 | 管道操作符串接 Prompt → LLM → OutputParser
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from comm.get_pass import get_pass

from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema import StrOutputParser

# 初始化 LLM（MiniMax 兼容接口）
llm = ChatOpenAI(
    model="MiniMax-M2.7",
    api_key=get_pass(),
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
