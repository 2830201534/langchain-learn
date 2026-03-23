"""
Day 1 综合练习：构建一个简单的 AI 助手
验收标准：能用 MiniMax API + PromptTemplate 动态变量 + 多消息构建完整对话
"""

from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema import SystemMessage, HumanMessage

def create_ai_assistant(api_key: str, base_url: str = "https://api.minimaxi.com/v1"):
    """创建 AI 助手实例"""
    llm = ChatOpenAI(
        model="MiniMax",
        api_key=api_key,
        base_url=base_url
    )
    
    system_template = PromptTemplate.from_template(
        "你是一个{role}，专门负责{topic}。请用专业且易懂的方式回答问题。"
    )
    
    def chat(user_input: str, role: str = "助手", topic: str = "通用问题") -> str:
        system_msg = system_template.invoke({"role": role, "topic": topic})
        response = llm.invoke([
            SystemMessage(content=system_msg.text),
            HumanMessage(content=user_input)
        ])
        return response.content
    
    return chat


if __name__ == "__main__":
    # TODO: 替换为你的 API Key
    API_KEY = "你的API Key"
    
    assistant = create_ai_assistant(API_KEY)
    
    # 测试对话
    print("=== 测试对话 ===")
    print(assistant(" LangChain 是什么？", role="AI讲师", topic="LangChain"))
