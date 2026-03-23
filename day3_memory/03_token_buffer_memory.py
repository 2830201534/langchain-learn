"""
Day 3 练习 3：ConversationTokenBufferMemory（按 Token 切）
当对话超过一定 token 数时，自动清除旧的历史
"""

from langchain_openai import ChatOpenAI
from langchain.memory import ConversationTokenBufferMemory

llm = ChatOpenAI(
    model="MiniMax",
    api_key="你的API Key",
    base_url="https://api.minimaxi.com/v1"
)

# 创建 Token 限制的 Memory（最大 100 token）
memory = ConversationTokenBufferMemory(
    llm=llm,
    max_token_limit=100
)

# 模拟对话
print("=== 添加多轮对话 ===")

conversations = [
    ("第1轮：我要查GMV数据，最近7天的，帮我算一下总和",
     "好的，正在为您查询近7天GMV数据..."),
    ("第2轮：按区域拆一下",
     "好的，按区域拆分数据..."),
    ("第3轮：加上环比上周的数据",
     "好的，正在计算环比数据..."),
    ("第4轮：导出成Excel",
     "好的，正在导出Excel文件..."),
    ("第5轮：发到我邮箱",
     "好的，已发送到您的邮箱..."),
]

for i, (user_input, ai_output) in enumerate(conversations, 1):
    memory.save_context({"input": user_input}, {"output": ai_output})
    print(f"第{i}轮完成")

print(f"\n=== Memory 消息数: {len(memory.chat_memory.messages)} ===")
print("\n=== 当前 Memory 变量 ===")
print(memory.load_memory_variables({}))
