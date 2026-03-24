"""
Day 4 练习 2：FAISS 向量数据库
将文档 Embedding 后存入 FAISS，支持相似度检索
"""

import sys
from pathlib import Path

from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from comm.get_pass import get_pass

# 注意：MiniMax 可能不支持 Embedding API，这里用 OpenAI 作为示例
# 实际使用时替换为支持的 Embedding 服务

EMBEDDING_CONFIG = {
    "model": "text-embedding-ada-002",  # 或其他支持的 embedding 模型
    "api_key": get_pass(),
    "base_url": "https://api.minimaxi.com/v1"  # 如果 MiniMax 支持 embedding
}

# 文档内容
documents = [
    "GMV定义：SUM(pay_amount)，过滤条件：status='paid'",
    "订单数量定义：COUNT(id)，无过滤条件",
    "用户数量定义：COUNT(DISTINCT user_id)，无过滤条件",
    "客单价定义：SUM(pay_amount)/COUNT(id)，过滤条件：status='paid'",
    "退款率定义：COUNT(refund_id)/COUNT(id)，过滤条件：status='refunded'"
]

# 创建 Embeddings（需要替换为实际可用的 Embedding 服务）
embeddings = OpenAIEmbeddings(**EMBEDDING_CONFIG)

# 存入 FAISS
db = FAISS.from_texts(documents, embeddings)

print("=== FAISS 向量数据库已创建 ===")
print(f"文档数量: {len(documents)}")

# 相似度检索
print("\n=== 检索测试 ===")

queries = [
    "GMV 怎么算？",
    "客单价是什么？",
    "用户数怎么统计？"
]

for query in queries:
    print(f"\n查询: {query}")
    results = db.similarity_search(query, k=2)  # 返回 top 2
    for i, doc in enumerate(results, 1):
        print(f"  结果{i}: {doc.page_content}")
