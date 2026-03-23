"""
Day 2 综合练习：构建翻译 Chain
验收标准：能用 LCEL 串出完整的翻译流程

示例场景：用户输入中文Query，自动翻译成英文执行SQL
"""

from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema import StrOutputParser

LLM_CONFIG = {
    "model": "MiniMax",
    "api_key": "你的API Key",
    "base_url": "https://api.minimaxi.com/v1"
}

def create_translation_chain():
    """构建翻译 Chain：中文 → 英文"""
    llm = ChatOpenAI(**LLM_CONFIG)
    
    return (
        PromptTemplate.from_template(
            """你是一个SQL专家。请把下面的自然语言查询转换成SQL。

要求：
1. 只输出SQL语句，不要其他解释
2. 表名是 orders，字段包括：id, user_id, pay_amount, status, created_at
3. status='paid' 表示已支付

中文查询：{query}

SQL："""
        )
        | llm
        | StrOutputParser()
    )


def create_nl2sql_chain():
    """构建完整的 NL2SQL Chain"""
    llm = ChatOpenAI(**LLM_CONFIG)
    
    # 翻译 Chain
    translate_prompt = PromptTemplate.from_template(
        "把以下中文翻译成英文：{query}"
    )
    
    # SQL 生成 Chain
    sql_prompt = PromptTemplate.from_template(
        """根据以下中文描述，生成 SQL 查询：

描述：{description}
表名：orders
字段：id, user_id, pay_amount, status, created_at

只输出SQL语句："""
    )
    
    translation_chain = translate_prompt | llm | StrOutputParser()
    sql_chain = sql_prompt | llm | StrOutputParser()
    
    # 组合 Chain
    return translation_chain | sql_chain


if __name__ == "__main__":
    chain = create_translation_chain()
    
    queries = [
        "近7天 GMV 是多少",
        "按区域统计订单数量",
        "今天新增了多少用户"
    ]
    
    print("=== NL2SQL 翻译测试 ===")
    for query in queries:
        sql = chain.invoke({"query": query})
        print(f"Q: {query}")
        print(f"A: {sql}\n")
