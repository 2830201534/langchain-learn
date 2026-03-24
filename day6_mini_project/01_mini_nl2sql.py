"""
Day 6 练习 1：最小化 NL2SQL Chain
从用户问题 → LLM → SQL 的最简路径
"""

import sys
from pathlib import Path

from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema import StrOutputParser
from langchain.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from comm.get_pass import get_pass

LLM_CONFIG = {
    "model": "MiniMax-M2.7",
    "api_key": get_pass(),
    "base_url": "https://api.minimaxi.com/v1"
}


# ============ 定义输出 Schema ============

class NL2SQLIntent(BaseModel):
    """NL2SQL 意图解析结果"""
    metric: str = Field(description="指标名称，如 GMV、订单数、用户数")
    aggregation: str = Field(description="聚合方式，如 SUM、COUNT、AVG")
    time_range: str = Field(description="时间范围，如 近7天、本月、2024年Q1")
    filters: Optional[str] = Field(default=None, description="过滤条件")
    group_by: Optional[str] = Field(default=None, description="分组维度，如 区域、渠道")


# ============ NL2SQL Chain ============

llm = ChatOpenAI(**LLM_CONFIG)

# Step 1: 意图解析
intent_parsing_prompt = PromptTemplate.from_template(
    """分析以下自然语言查询，提取关键信息。

查询：{query}

表结构：
- orders: id, user_id, pay_amount, status, created_at, region

输出 JSON，包含：
- metric: 指标名称
- aggregation: 聚合方式
- time_range: 时间范围
- filters: 过滤条件（可选）
- group_by: 分组维度（可选）

JSON："""
)

intent_chain = (
    intent_parsing_prompt
    | llm
    | JsonOutputParser(pydantic_model=NL2SQLIntent)
)

# Step 2: SQL 生成
sql_generation_prompt = PromptTemplate.from_template(
    """根据以下意图信息，生成 SQL 查询。

意图信息：
{intent}

表名：orders
字段：id, user_id, pay_amount, status, created_at, region
status='paid' 表示已支付

只输出 SQL 语句，不需要其他内容：

SQL："""
)

sql_chain = (
    sql_generation_prompt
    | llm
    | StrOutputParser()
)

# 组合成完整 NL2SQL Chain
nl2sql_chain = intent_chain | sql_chain


# ============ 测试 ============

if __name__ == "__main__":
    queries = [
        "近7天 GMV 是多少",
        "按区域统计订单数量",
        "今天新增了多少用户"
    ]
    
    print("=== NL2SQL Chain 测试 ===\n")
    
    for query in queries:
        print(f"查询: {query}")
        
        # 解析意图
        intent = intent_chain.invoke({"query": query})
        print(f"意图: {intent}")
        
        # 生成 SQL
        sql = sql_chain.invoke({"intent": intent})
        print(f"SQL: {sql}\n")
