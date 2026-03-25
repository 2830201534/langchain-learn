"""
Day 5 练习 3：Agent 决策循环详解
深入理解 Agent 的工作流程：思考 → 行动 → 观察 → ... → 最终回答
"""

import sys
from pathlib import Path

from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import tool
from langchain.agents.format_scratchpad import format_to_openai_function_messages

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from comm.get_pass import get_pass

LLM_CONFIG = {
    "model": "MiniMax-M2.7",
    "api_key": get_pass(),
    "base_url": "https://api.minimaxi.com/v1"
}

@tool
def get_current_time() -> str:
    """获取当前时间"""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@tool
def search_web(query: str) -> str:
    """搜索互联网"""
    # 模拟搜索结果
    return f"搜索结果：关于「{query}」的信息..."


@tool
def calculate(expr: str) -> str:
    """执行数学计算"""
    try:
        result = eval(expr)
        return str(result)
    except:
        return "计算错误"


tools = [get_current_time, search_web, calculate]

llm = ChatOpenAI(**LLM_CONFIG)

# 带详细步骤的 Prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", """你是一个智能助手。

工作流程：
1. 理解用户问题
2. 决定是否需要调用工具
3. 如果需要，选择合适的工具并生成参数
4. 根据工具返回结果生成回答

可用工具：
- get_current_time: 获取当前时间
- search_web: 搜索互联网
- calculate: 执行数学计算（输入 Python 表达式）"""),
    MessagesPlaceholder(variable_name="chat_history", optional=True),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad")
])

agent = create_openai_functions_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

print("=== Agent 决策循环测试 ===\n")

test_questions = [
    "现在几点了？",
    "什么是 LangChain？",
    "计算 (100 + 200) * 3 的结果"
]

for q in test_questions:
    print(f"Q: {q}")
    result = agent_executor.invoke({"input": q})
    print(f"A: {result['output']}\n")
