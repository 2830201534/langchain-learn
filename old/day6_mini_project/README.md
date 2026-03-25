# Day 6: LangChain 完整项目演练 + 架构设计

## 目标
用 LangChain 从头实现一遍 NL2SQL 核心流程，验证可行性

## 任务清单
- [ ] 用 LangChain 实现一个最小化的 NL2SQL Chain
- [ ] 对比 Python 版和 Java 版的架构差异
- [ ] 确定下周末重构的方案：全部用 Python 还是 Java + Python 混合

## 验收标准
在 Python 里跑通一个完整的多轮对话查数流程，能正确处理追问

## 核心架构
```
用户问题 → Memory（上下文） → Prompt（含 metadata） → LLM → Intent JSON
Intent JSON → SQL Compiler（确定性） → 执行 → 返回结果
```
