"""
Day 2 练习 2：多步 Chain（链式调用）
将多个 LLM 调用串联，形成多步处理流程
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from comm.get_pass import get_pass

from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema import StrOutputParser

llm = ChatOpenAI(
    model="MiniMax-M2.7",
    api_key=get_pass(),
    base_url="https://api.minimaxi.com/v1"
)

# Step 1: 中文 → 英文
step1_translate = (
    PromptTemplate.from_template("把以下中文翻译成英文：{text}")
    | llm
    | StrOutputParser()
)

# Step 2: 英文 → 中文（意译）
step2_paraphrase = (
    PromptTemplate.from_template("请用更优雅的方式表达以下英文：{text}")
    | llm
    | StrOutputParser()
)

# Step 3: 总结
step3_summarize = (
    PromptTemplate.from_template("用一句话总结：{text}")
    | llm
    | StrOutputParser()
)

# 串联三步
chain = step1_translate | step2_paraphrase | step3_summarize

result = chain.invoke({"text": "今天天气真好"})
print("=== 三步 Chain 结果 ===")
print(f"原文: 今天天气真好")
print(f"最终结果: {result}")
