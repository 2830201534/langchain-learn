"""
Day 3 练习 2：ConversationSummaryMemory（摘要压缩）
对话历史太长时自动摘要，节省 token
"""

from langchain_openai import ChatOpenAI
from langchain.memory import ConversationSummaryMemory

llm = ChatOpenAI(
    model="MiniMax",
    api_key="你的API Key",
    base_url="https://api.minimaxi.com/v1"
)

# 创建摘要 Memory
memory = ConversationSummaryMemory(llm=llm)

# 模拟多轮对话
print("=== 对话进行中 ===")

inputs = [
    "我要查最近7天的GMV数据",
    "按区域拆一下",
    "加上环比数据",
    "导出Excel"
]

for user_input in inputs:
    memory.save_context({"input": user_input}, {"output": f"已处理: {user_input}"})
    print(f"用户: {user_input}")

print("\n=== Memory 中的变量 ===")
print(memory.chat_memory)

print("\n=== 生成的摘要 ===")
print(memory.load_memory_variables({}))
