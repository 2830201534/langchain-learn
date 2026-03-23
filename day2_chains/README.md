# Day 2: Chains（LCEL）

## 目标
理解 LangChain 的 Chain 机制，学会用 LCEL 管道语法串接 Prompt → LLM

## 任务清单
- [ ] 理解 `RunnableSequence`（LCEL 管道）
- [ ] 掌握 `|` 管道操作符：`prompt | llm | output_parser`
- [ ] 学会用 `chain.invoke()` 和 `chain.stream()` 调用
- [ ] 完成练习：构建一个"翻译 Chain"，输入中文，输出英文

## 验收标准
能用 LCEL 串出完整的 Prompt → Model → Parser 链路
