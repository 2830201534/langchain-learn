"""
Day 5 练习 2：OpenAI Functions Agent
使用 Functions Agent，让模型自主选择调用哪个 Tool
"""

import sys
from pathlib import Path

from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import tool

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from comm.get_pass import get_pass

LLM_CONFIG = {
    "model": "MiniMax-M2.7",
    "api_key": get_pass(),
    "base_url": "https://api.minimaxi.com/v1"
}

# 定义 Tools
@tool
def get_gmv(days: int) -> str:
    """查询近 N 天的 GMV 数据"""
    return f"近{days}天 GMV: ¥{days * 12345:.2f}"


@tool
def get_order_count(days: int) -> str:
    """查询近 N 天的订单数量"""
    return f"近{days}天 订单数：{days * 5678}"


tools = [get_gmv, get_order_count]

# 创建 LLM 并绑定 Tools
llm = ChatOpenAI(**LLM_CONFIG)
llm_with_tools = llm.bind_tools(tools)

# 创建 Prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个数据查询助手，可以帮助用户查询业务数据。"),
    MessagesPlaceholder(variable_name="chat_history", optional=True),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad")
])

# 创建 Agent - 使用通用的 create_tool_calling_agent
agent = create_tool_calling_agent(llm_with_tools, tools, prompt)

# 创建 Agent Executor
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True
)

print("=== Functions Agent 测试 ===\n")

# 测试 1：查询 GMV
print("Q: 近 7 天 GMV 是多少？")
result = agent_executor.invoke({"input": "近 7 天 GMV 是多少？"})
print(f"A: {result['output']}\n")

# 测试 2：查询订单
print("Q: 近 30 天有多少订单？")
result = agent_executor.invoke({"input": "近 30 天有多少订单？"})
print(f"A: {result['output']}\n")

# 测试 3：通用问题（不需要调用 Tool）
print("Q: 你叫什么名字？")
result = agent_executor.invoke({"input": "你叫什么名字？"})
print(f"A: {result['output']}")

# 测试 4：扩展问题
print("Q: 近10天订单收货量？")
result = agent_executor.invoke({"input": "近10天订单收货量？"})
print(f"A: {result['output']}")