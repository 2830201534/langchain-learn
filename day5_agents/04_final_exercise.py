"""
Day 5 综合练习：构建数据查询 Agent
验收标准：
- 能回答"查 GMV"、"查订单"等数据查询问题
- 能回答"你是谁"等通用问题
- Agent 自主决定调用哪个 Tool

这是 codex RouteDecision（四路路由）的 Agent 版本
"""

from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import tool

LLM_CONFIG = {
    "model": "MiniMax",
    "api_key": "你的API Key",
    "base_url": "https://api.minimaxi.com/v1"
}


# ============ Tools ============

@tool
def query_gmv(days: int = 7) -> str:
    """查询近N天的GMV
    
    Args:
        days: 天数，默认7天
        
    Returns:
        GMV 数据字符串
    """
    gmv = days * 50000  # 模拟数据
    return f"近{days}天 GMV: ¥{gmv:,}"


@tool
def query_orders(days: int = 7) -> str:
    """查询近N天的订单
    
    Args:
        days: 天数，默认7天
        
    Returns:
        订单数据字符串
    """
    orders = days * 1000  # 模拟数据
    return f"近{days}天 订单数: {orders:,}"


@tool
def query_users(days: int = 7) -> str:
    """查询近N天的用户数
    
    Args:
        days: 天数，默认7天
        
    Returns:
        用户数据字符串
    """
    users = days * 200  # 模拟数据
    return f"近{days}天 活跃用户: {users:,}"


@tool
def calculate(expr: str) -> str:
    """数学计算器
    
    Args:
        expr: Python 数学表达式，如 "100*2+50"
        
    Returns:
        计算结果
    """
    try:
        result = eval(expr)
        return f"计算结果: {result}"
    except Exception as e:
        return f"计算错误: {e}"


tools = [query_gmv, query_orders, query_users, calculate]


# ============ Agent ============

class DataQueryAgent:
    """数据查询 Agent - 类似 codex RouteDecision 的 Agent 版本"""
    
    def __init__(self):
        self.llm = ChatOpenAI(**LLM_CONFIG)
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个智能数据查询助手，可以帮助用户查询业务数据。

你能做的：
- 查询 GMV、订单、用户等业务指标
- 执行数学计算
- 回答通用问题

当用户问数据相关问题时，自主选择合适的工具调用。
当用户问通用问题时，直接回答，不需要调用工具。"""),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        self.agent = create_openai_functions_agent(self.llm, tools, self.prompt)
        self.executor = AgentExecutor(
            agent=self.agent,
            tools=tools,
            verbose=True
        )
    
    def chat(self, question: str) -> str:
        """对话"""
        result = self.executor.invoke({"input": question})
        return result["output"]


if __name__ == "__main__":
    agent = DataQueryAgent()
    
    print("=== 数据查询 Agent 测试 ===\n")
    
    questions = [
        "近7天 GMV 是多少？",
        "今天有多少订单？",
        "100 + 200 * 3 等于多少？",
        "你是谁？",
        "给我介绍一下你自己"
    ]
    
    for q in questions:
        print(f"Q: {q}")
        a = agent.chat(q)
        print(f"A: {a}\n")
