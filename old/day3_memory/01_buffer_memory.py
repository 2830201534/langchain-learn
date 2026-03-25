"""
Day 3 练习 1：ConversationBufferMemory（全量历史）
最简单的 Memory 方式，保存所有对话历史
"""

import sys
from pathlib import Path

from langchain_openai import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from comm.get_pass import get_pass

llm = ChatOpenAI(
    model="MiniMax-M2.7",
    api_key=get_pass(),
    base_url="https://api.minimaxi.com/v1"
)

# 创建 Memory
memory = ConversationBufferMemory()

# 创建对话 Chain（自动整合 Memory）
conversation = ConversationChain(
    llm=llm,
    memory=memory,
    verbose=True
)

# 多轮对话
print("=== 第1轮 ===")
response = conversation.predict(input="我叫张三")
print(f"AI: {response}")

print("\n=== 第2轮 ===")
response = conversation.predict(input="我叫什么名字？")
print(f"AI: {response}")

print("\n=== 打印 Memory ===")
print(memory.chat_memory.messages)
