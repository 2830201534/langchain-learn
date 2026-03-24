"""
Day 6 练习 3：完整 NL2SQL Pipeline
包含：意图解析 → SQL 生成 → SQL 执行 → 结果返回
"""

import sys
from pathlib import Path

from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema import StrOutputParser
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain
from langchain.output_parsers import JsonOutputToolsParser
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from comm.get_pass import get_pass

LLM_CONFIG = {
    "model": "MiniMax-M2.7",
    "api_key": get_pass(),
    "base_url": "https://api.minimaxi.com/v1"
}


class NL2SQLIntent(BaseModel):
    metric: str = Field(description="指标名称")
    aggregation: str = Field(description="聚合方式：SUM/COUNT/AVG/MAX/MIN")
    time_range: str = Field(description="时间范围")
    filters: Optional[str] = Field(default=None, description="过滤条件 SQL")
    group_by: Optional[str] = Field(default=None, description="分组维度")


class NL2SQLPipeline:
    """完整的 NL2SQL Pipeline
    
    流程：
    1. 用户问题 → Intent（LLM 解析）
    2. Intent → SQL（LLM 生成）
    3. SQL 执行 → 结果（模拟）
    4. 结果 → 自然语言（LLM 总结）
    """
    
    def __init__(self):
        self.llm = ChatOpenAI(**LLM_CONFIG)
        self.memory = ConversationBufferMemory(
            memory_key="history",
            return_messages=True
        )
        
        # Intent 解析 Chain
        self.intent_chain = LLMChain(
            llm=self.llm,
            prompt=PromptTemplate.from_template(
                """分析查询，提取信息。处理指代词。

历史：{history}
查询：{query}

表：orders(id, user_id, pay_amount, status, created_at, region)

JSON："""
            ),
            output_parser=JsonOutputToolsParser(pydantic_model=NL2SQLIntent),
            memory=self.memory
        )
        
        # SQL 生成 Chain
        self.sql_chain = LLMChain(
            llm=self.llm,
            prompt=PromptTemplate.from_template(
                """意图转 SQL。

意图：{intent}

表：orders(id, user_id, pay_amount, status, created_at, region)
status='paid' 是已支付

只输出 SQL："""
            ),
            output_parser=StrOutputParser()
        )
        
        # 结果生成 Chain
        self.result_chain = LLMChain(
            llm=self.llm,
            prompt=PromptTemplate.from_template(
                """根据查询和结果，用自然语言回答。

查询：{query}
SQL结果：{result}

回答："""
            ),
            output_parser=StrOutputParser()
        )
    
    def execute_sql_mock(self, sql: str) -> List[Dict[str, Any]]:
        """模拟 SQL 执行（实际项目替换为真实数据库）"""
        # 模拟返回数据
        if "SUM" in sql and "pay_amount" in sql:
            return [{"gmv": 1234567.89, "period": "近7天"}]
        elif "COUNT" in sql and "id" in sql:
            return [{"order_count": 5678, "period": "近7天"}]
        elif "COUNT(DISTINCT" in sql and "user_id" in sql:
            return [{"user_count": 1234, "period": "近7天"}]
        elif "GROUP BY" in sql:
            return [
                {"region": "华东", "gmv": 500000},
                {"region": "华北", "gmv": 300000},
                {"region": "华南", "gmv": 434567.89}
            ]
        return [{"result": "No data"}]
    
    def chat(self, query: str) -> str:
        """处理完整流程"""
        # 1. 解析意图
        intent = self.intent_chain.invoke({"query": query})
        
        # 2. 生成 SQL
        sql = self.sql_chain.invoke({"intent": intent})
        
        # 3. 执行 SQL
        raw_result = self.execute_sql_mock(sql)
        
        # 4. 生成自然语言结果
        result = self.result_chain.invoke({
            "query": query,
            "result": str(raw_result)
        })
        
        return result


if __name__ == "__main__":
    pipeline = NL2SQLPipeline()
    
    print("=== 完整 NL2SQL Pipeline 测试 ===\n")
    
    queries = [
        "近7天 GMV 是多少？",
        "按区域看一下",
        "还是刚才那个指标，加上环比"
    ]
    
    for q in queries:
        print(f"Q: {q}")
        result = pipeline.chat(q)
        print(f"A: {result}\n")
