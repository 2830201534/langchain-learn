# Day1 练习题：LangChain 核心基础

> 🎯 练习目标：掌握 Models、PromptTemplate、Messages、LCEL 基础用法
> ⏰ 预计时间：45~60 分钟
> 📝 要求：所有代码必须实际运行，截图或复制输出到练习文件末尾

---

## 练习1：模型初始化（⭐）
**目标**：熟练掌握 MiniMax 模型的初始化方式

```python
# 参考代码：
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from comm.get_pass import get_pass
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="MiniMax-M2.7",
    api_key=get_pass(),
    base_url="https://api.minimaxi.com/v1"
)

# 调用测试
response = llm.invoke("你好，介绍一下自己")
print(response.content)
```

**任务**：
1. 新建文件 `practice_01_model_init.py`
2. 复制以上代码并运行
3. 把输出结果截图或复制到练习文件

---

## 练习2：PromptTemplate 变量注入（⭐）
**目标**：掌握模板变量的使用方式

**任务**：
1. 新建文件 `practice_02_prompt_template.py`
2. 实现以下功能：
   - 创建模板：`我叫{name}，今年{age}岁，从事{job}`
   - 用不同参数调用模板
   - 调用 LLM 生成回复

**验收标准**：
- ✅ 模板变量正确替换
- ✅ LLM 返回合理回复

---

## 练习3：多消息组合（⭐⭐）
**目标**：掌握 SystemMessage + HumanMessage 的组合用法

**任务**：
1. 新建文件 `practice_03_messages.py`
2. 实现一个"Python 讲师"角色：
   - SystemMessage：设定角色为"资深Python讲师，说话幽默"
   - HumanMessage：问"什么是生成器？"
3. 对比有/无 SystemMessage 的回答差异

**验收标准**：
- ✅ 能观察到角色设定的效果
- ✅ 两次回答有显著差异

---

## 练习4：LCEL 链式调用（⭐⭐⭐）
**目标**：掌握 LCEL 管道串联的核心语法

**任务**：
1. 新建文件 `practice_04_lcel_chain.py`
2. 实现一个"翻译 → 总结 → 情感分析"的三步链

```python
# 伪代码结构：
# step1 = 翻译链（中文→英文）
# step2 = 总结链（英文→一句话总结）
# step3 = 情感分析链（判断情感正负）
# chain = step1 | step2 | step3
```

**验收标准**：
- ✅ 三步链能正常工作
- ✅ 数据在步骤间正确传递
- ✅ 能用 `invoke()` 调用

---

## 练习5：LCEL 流式输出（⭐⭐⭐）
**目标**：掌握流式调用的用法

**任务**：
1. 新建文件 `practice_05_stream.py`
2. 实现流式调用 LLM
3. 对比 `invoke()` 和 `stream()` 的输出差异

**验收标准**：
- ✅ `stream()` 能逐步输出字符
- ✅ 感受到流式输出的"打字机"效果

---

## 练习6：OutputParser 输出解析（⭐⭐⭐⭐）
**目标**：掌握 StrOutputParser 和 JsonOutputParser 的使用

**任务**：
1. 新建文件 `practice_06_output_parser.py`
2. 实现：
   - 用 `StrOutputParser` 获取纯文本输出
   - 用 `JsonOutputParser` 解析结构化 JSON

```python
# JsonOutputParser 示例（解析为 Pydantic 模型）
from pydantic import BaseModel, Field

class WeatherInfo(BaseModel):
    city: str = Field(description="城市名称")
    temperature: float = Field(description="温度")
    condition: str = Field(description="天气状况")
```

**验收标准**：
- ✅ StrOutputParser 返回纯字符串
- ✅ JsonOutputParser 正确解析 JSON 为 Pydantic 对象

---

## 练习7：综合实战 - NL2SQL 意图解析（⭐⭐⭐⭐⭐）
**目标**：综合运用 LCEL + PromptTemplate + JsonOutputParser

**任务**：
1. 新建文件 `practice_07_nl2sql_intent.py`
2. 实现 NL2SQL 意图解析链：
   - 输入："近7天GMV是多少"
   - 输出：结构化的意图信息（metric, aggregation, time_range, filters）

```python
# 期望输出结构：
{
    "metric": "GMV",
    "aggregation": "SUM",
    "time_range": "近7天",
    "filters": "status='paid'"
}
```

**验收标准**：
- ✅ LLM 输出符合预期的 JSON 结构
- ✅ JsonOutputParser 正确解析

---

## 练习8：挑战题 - RunnableLambda 自定义函数（⭐⭐⭐⭐⭐）
**目标**：掌握将普通函数接入 LCEL 链

**任务**：
1. 新建文件 `practice_08_runnable_lambda.py`
2. 实现：
   - 创建一个自定义函数，对 LLM 输出进行"格式化"（如加框、加 emoji）
   - 用 `RunnableLambda` 将函数接入 LCEL 链

**提示**：
```python
from langchain_core.runnables import RunnableLambda

def add_format(text: str) -> str:
    return f"📝 结果：\n{'='*20}\n{text}\n{'='*20}"

chain = (
    PromptTemplate.from_template("翻译：{text}")
    | llm
    | StrOutputParser()
    | RunnableLambda(add_format)  # 自定义格式化
)
```

**验收标准**：
- ✅ 函数能正确接入 LCEL 链
- ✅ 输出带有自定义格式

---

## 输出要求

完成所有练习后：
1. 创建文件 `practice_summary.md`
2. 记录每个练习的：
   - 练习编号和名称
   - 运行结果（截图或输出复制）
   - 遇到的问题和解决方法
3. 在最后写下：
   - 今天最深刻的概念理解
   - 遇到的主要问题
   - 下一阶段学习计划
