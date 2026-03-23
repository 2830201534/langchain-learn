# Day 5: Agents（自主决策）

## 目标
理解 Tool Calling + Agent 决策循环，理解模型如何决定调用工具

## 任务清单
- [ ] 理解什么是 Tool（函数作为工具）
- [ ] 跑通 `initialize_agent` + `MRKLChain`（或 OpenAI Functions Agent）
- [ ] 理解 Agent 是"循环"：模型决定调用工具 → 工具返回结果 → 模型决定下一步
- [ ] 完成练习：构建一个 Agent，能回答"查 GMV"，也能回答"你是谁"

## 验收标准
Agent 能根据问题类型自主选择"查数据库"还是"通用问答"

## 重要概念
这个对应 codex 的 `RouteDecision`（四路路由）——但 Agent 版本是模型自己决定，不是硬编码 if-else
