"""
Day 5 练习 1：Tool 基础
将函数定义为 Tool，供 Agent 调用
"""

import sys
from pathlib import Path

from langchain.tools import tool
from langchain_openai import ChatOpenAI

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from comm.get_pass import get_pass

LLM_CONFIG = {
    "model": "MiniMax-M2.7",
    "api_key": get_pass(),
    "base_url": "https://api.minimaxi.com/v1"
}

# 定义 Tool（使用 @tool 装饰器）
@tool
def get_gmv(days: int) -> str:
    """查询近N天的GMV数据
    
    Args:
        days: 天数，如 7 表示近7天
        
    Returns:
        GMV数据字符串
    """
    # 模拟数据库查询
    return f"近{days}天 GMV: ¥{days * 12345:.2f}"


@tool
def get_order_count(days: int) -> str:
    """查询近N天的订单数量
    
    Args:
        days: 天数，如 7 表示近7天
        
    Returns:
        订单数量字符串
    """
    return f"近{days}天 订单数: {days * 5678}"


@tool
def calculate_compound_interest(principal: float, rate: float, years: int) -> str:
    """计算复利
    
    Args:
        principal: 本金
        rate: 年利率（百分比，如 5 表示 5%）
        years: 年数
        
    Returns:
        复利计算结果
    """
    amount = principal * (1 + rate / 100) ** years
    return f"本金 {principal}，年利率 {rate}%，{years}年后本息合计: {amount:.2f}"


# 测试 Tool
print("=== Tool 测试 ===")
print(get_gmv.invoke({"days": 7}))
print(get_order_count.invoke({"days": 30}))
print(calculate_compound_interest.invoke({"principal": 10000, "rate": 5, "years": 10}))
