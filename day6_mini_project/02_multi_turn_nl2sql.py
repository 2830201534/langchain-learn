"""
Day 6 练习 2：带 Memory 的多轮 NL2SQL
实现：用户第1轮问GMV，第2轮问区域，第3轮说"还是刚才那个指标"
"""

from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema import StrOutputParser, HumanMessage
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain
from langchain.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import Optional

LLM_CONFIG = {
    "model": "MiniMax",
    "api_key": "你的API Key",
    "base_url": "https://api.minimaxi.com/v1"
}


# ============ Schema ============

class NL2SQLIntent(BaseModel):
    metric: str = Field(description="指标名称")
    aggregation: str = Field(description="聚合方式")
    time_range: str = Field(description="时间范围")
    filters: Optional[str] = Field(default=None, description="过滤条件")
    group_by: Optional[str] = Field(default=None, description="分组维度")


# ============ 多轮 NL2SQL Chain ============

class MultiTurnNL2SQL:
    """带 Memory 的多轮 NL2SQL"""
    
    def __init__(self):
        self.llm = ChatOpenAI(**LLM_CONFIG)
        
        # Memory
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # 意图解析 Chain
        self.intent_parsing_chain = LLMChain(
            llm=self.llm,
            prompt=PromptTemplate.from_template(
                """分析以下查询，提取关键信息。注意处理指代词（如"刚才那个指标"）。

历史上下文：
{chat_history}

当前查询：{query}

表结构：orders(id, user_id, pay_amount, status, created_at, region)

JSON格式：
{
    "metric": "指标名",
    "aggregation": "聚合方式",
    "time_range": "时间范围",
    "filters": "过滤条件（可选）",
    "group_by": "分组维度（可选）"
}

JSON："""
            ),
            output_parser=JsonOutputParser(pydantic_model=NL2SQLIntent),
            memory=self.memory
        )
        
        # SQL 生成 Chain
        self.sql_chain = LLMChain(
            llm=self.llm,
            prompt=PromptTemplate.from_template(
                """根据以下意图信息生成 SQL。

意图：
{intent}

表名：orders
字段：id, user_id, pay_amount, status, created_at, region
status='paid' 表示已支付

只输出 SQL："""
            ),
            output_parser=StrOutputParser()
        )
    
    def chat(self, query: str) -> str:
        """处理查询"""
        # 解析意图（自动保存到 Memory）
        intent = self.intent_parsing_chain.invoke({"query": query})
        
        # 生成 SQL
        sql = self.sql_chain.invoke({"intent": intent})
        
        return sql
    
    def show_history(self):
        """查看历史"""
        return self.memory.chat_memory.messages


if __name__ == "__main__":
    bot = MultiTurnNL2SQL()
    
    print("=== 多轮 NL2SQL 测试 ===\n")
    
    # 第1轮
    print("第1轮 - 用户：查GMV")
    sql = bot.chat("查GMV，近7天的")
    print(f"SQL: {sql}\n")
    
    # 第2轮
    print("第2轮 - 用户：按区域拆一下")
    sql = bot.chat("按区域拆一下")
    print(f"SQL: {sql}\n")
    
    # 第3轮（关键：能否理解"那个指标"指GMV）
    print("第3轮 - 用户：还是刚才那个指标，加上环比数据")
    sql = bot.chat("还是刚才那个指标，加上环比数据")
    print(f"SQL: {sql}\n")
    
    print("=== 对话历史 ===")
    for msg in bot.show_history():
        print(f"{msg.type}: {msg.content[:80]}...")
