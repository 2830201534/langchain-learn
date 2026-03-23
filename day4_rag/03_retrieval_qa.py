"""
Day 4 练习 3：RetrievalQA Chain
检索 → 构建 Context → 生成回答 的完整 RAG 链路
"""

from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain.vectorstores import FAISS

LLM_CONFIG = {
    "model": "MiniMax",
    "api_key": "你的API Key",
    "base_url": "https://api.minimaxi.com/v1"
}

EMBEDDING_CONFIG = {
    "model": "text-embedding-ada-002",
    "api_key": "你的API Key",
    "base_url": "https://api.minimaxi.com/v1"
}

# 知识库文档（codex 指标定义）
knowledge_base = [
    "GMV（成交总额）：计算公式 SUM(pay_amount)，过滤条件 status='paid'，按 created_at 统计",
    "订单数量：计算公式 COUNT(id)，无过滤条件，按 created_at 统计",
    "用户数量：计算公式 COUNT(DISTINCT user_id)，无过滤条件，按 created_at 统计",
    "客单价：计算公式 SUM(pay_amount)/COUNT(id)，过滤条件 status='paid'",
    "退款订单数：计算公式 COUNT(id)，过滤条件 status='refunded'",
    "毛利率：计算公式 (收入-成本)/收入*100%，无过滤条件",
]

# 构建向量数据库
embeddings = OpenAIEmbeddings(**EMBEDDING_CONFIG)
db = FAISS.from_texts(knowledge_base, embeddings)

# 创建 Retriever
retriever = db.as_retriever(search_kwargs={"k": 2})  # 返回 top 2 相关文档

# 创建 LLM
llm = ChatOpenAI(**LLM_CONFIG)

# 创建 RetrievalQA Chain
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",  # 将检索到的文档拼接到 prompt
    retriever=retriever,
    verbose=True
)

print("=== RAG 问答测试 ===\n")

questions = [
    "GMV 的计算口径是什么？",
    "客单价怎么算？",
    "用户数量怎么统计？"
]

for question in questions:
    print(f"Q: {question}")
    result = qa_chain.invoke({"query": question})
    print(f"A: {result['result']}\n")
