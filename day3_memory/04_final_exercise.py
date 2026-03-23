"""
Day 3 综合练习：构建多轮对话 Bot
验收标准：
- 第1轮说"查GMV"
- 第2轮说"按区域"
- 第3轮说"还是刚才那个指标"
- 模型能理解"刚才那个指标"指的是GMV
"""

from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain.schema import SystemMessage

LLM_CONFIG = {
    "model": "MiniMax",
    "api_key": "你的API Key",
    "base_url": "https://api.minimaxi.com/v1"
}

class MultiTurnQueryBot:
    """多轮对话 Bot，能记住上下文"""
    
    def __init__(self):
        self.llm = ChatOpenAI(**LLM_CONFIG)
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # 带 Memory 的 Chain
        self.chain = LLMChain(
            llm=self.llm,
            prompt=PromptTemplate.from_template(
                """你是一个数据查询助手，专注于 SQL 查询生成。

历史对话：
{chat_history}

当前问题：{query}

要求：
1. 理解"刚才/之前/那个指标"等指代词指向什么
2. 只输出 SQL 语句，不输出其他内容
3. 表名：orders，字段：id, user_id, pay_amount, status, created_at, region
4. status='paid' 表示已支付

SQL："""
            ),
            memory=self.memory,
            verbose=True
        )
    
    def chat(self, query: str) -> str:
        """发送消息并获取回复"""
        result = self.chain.invoke({"query": query})
        return result["text"]
    
    def show_history(self):
        """显示对话历史"""
        return self.memory.chat_memory.messages


if __name__ == "__main__":
    bot = MultiTurnQueryBot()
    
    print("=== 多轮对话测试 ===\n")
    
    # 第1轮
    print("第1轮 - 用户：查GMV")
    result = bot.chat("查GMV，最近7天")
    print(f"AI SQL: {result}\n")
    
    # 第2轮
    print("第2轮 - 用户：按区域拆一下")
    result = bot.chat("按区域拆一下")
    print(f"AI SQL: {result}\n")
    
    # 第3轮（关键：能否理解"那个指标"指GMV）
    print("第3轮 - 用户：还是刚才那个指标，加上环比")
    result = bot.chat("还是刚才那个指标，加上环比")
    print(f"AI SQL: {result}\n")
    
    print("=== 完整对话历史 ===")
    for msg in bot.show_history():
        print(f"{msg.type}: {msg.content[:50]}...")
