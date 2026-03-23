"""
Day 4 综合练习：基于 codex 指标定义的 RAG 问答系统
验收标准：问"GMV 的口径是什么"，能正确回答

这是 codex 里 SemanticQueryCatalogSnapshot 的 LangChain 版本
"""

from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain.vectorstores import FAISS
from langchain.prompts import PromptTemplate

LLM_CONFIG = {
    "model": "MiniMax",
    "api_key": "你的API Key",
    "base_url": "https://api.minimaxi.com/v1"
}

# 模拟 codex 的指标定义知识库
METRICS_KNOWLEDGE = """
# Codex 指标定义知识库

## GMV（成交总额）
- 计算公式：SUM(pay_amount)
- 过滤条件：status = 'paid'
- 时间字段：created_at
- 描述：所有已完成支付订单的金额总和

## 订单数量
- 计算公式：COUNT(id)
- 过滤条件：无
- 时间字段：created_at
- 描述：所有订单的总数量（含取消）

## 有效订单
- 计算公式：COUNT(id)
- 过滤条件：status IN ('paid', 'shipped', 'delivered')
- 时间字段：created_at
- 描述：处于正向流转状态的订单

## 用户数量
- 计算公式：COUNT(DISTINCT user_id)
- 过滤条件：无
- 时间字段：created_at
- 描述：去重后的下单用户数

## 客单价
- 计算公式：SUM(pay_amount) / COUNT(DISTINCT user_id)
- 过滤条件：status = 'paid'
- 时间字段：created_at
- 描述：平均每个用户的消费金额

## 退款率
- 计算公式：COUNT(CASE WHEN status='refunded' THEN 1 END) / COUNT(id)
- 过滤条件：无
- 时间字段：created_at
- 描述：退款订单占总订单的比例
"""


class CodexMetricRAG:
    """基于 Codex 指标定义的 RAG 问答系统"""
    
    def __init__(self):
        # LLM
        self.llm = ChatOpenAI(**LLM_CONFIG)
        
        # Embeddings（需要替换为实际可用的 Embedding 服务）
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-ada-002",
            api_key="你的API Key",
            base_url="https://api.minimaxi.com/v1"
        )
        
        # 构建知识库
        self.db = FAISS.from_texts(
            METRICS_KNOWLEDGE.strip().split("\n## "),
            self.embeddings
        )
        
        # Retriever
        self.retriever = self.db.as_retriever(search_kwargs={"k": 2})
        
        # 自定义 Prompt
        custom_prompt = PromptTemplate(
            template="""基于以下指标定义知识库，回答用户问题。

知识库：
{context}

问题：{question}

要求：
1. 只根据知识库中的定义回答
2. 回答要包含计算公式和过滤条件
3. 如果知识库中没有相关信息，说明不知道

回答：""",
            input_variables=["context", "question"]
        )
        
        # 构建 QA Chain
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.retriever,
            prompt=custom_prompt,
            return_source_documents=True
        )
    
    def ask(self, question: str) -> dict:
        """提问并获取回答"""
        result = self.qa_chain.invoke({"query": question})
        return {
            "answer": result["result"],
            "sources": [doc.page_content for doc in result["source_documents"]]
        }


if __name__ == "__main__":
    rag = CodexMetricRAG()
    
    print("=== Codex 指标定义 RAG 问答测试 ===\n")
    
    questions = [
        "GMV 的口径是什么？",
        "客单价怎么计算？",
        "退款率怎么算？"
    ]
    
    for question in questions:
        print(f"Q: {question}")
        result = rag.ask(question)
        print(f"A: {result['answer']}")
        print(f"来源: {result['sources']}\n")
