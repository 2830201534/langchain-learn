"""
Day 1 练习 1：基础 API 调用
用 MiniMax API 调用 ChatOpenAI 兼容接口
"""

import sys
from pathlib import Path

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from comm.get_pass import get_pass

# 初始化 LLM（MiniMax 兼容接口）
llm = ChatOpenAI(
    model="MiniMax-M2.7",
    api_key=get_pass(),
    base_url="https://api.minimaxi.com/v1"
)


# 简单调用
response = llm.invoke([HumanMessage(content="你好，请介绍一下自己 详细介绍自己是哪个模型")])
print("=== 简单调用结果 ===")
print(response.content)
