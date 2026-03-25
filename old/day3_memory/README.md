# Day 3: Memory（对话记忆）

## 目标
理解 LangChain 的 Memory 体系，这是你当前 codex 最缺的部分

## 任务清单
- [ ] 跑通 `ConversationBufferMemory`（全量历史）
- [ ] 跑通 `ConversationSummaryMemory`（摘要压缩）
- [ ] 理解 `ConversationTokenBufferMemory`（按 token 切）
- [ ] 完成练习：构建一个多轮对话 Bot，第 3 轮能引用第 1 轮的信息

## 验收标准
用户第 1 轮说"查 GMV"，第 2 轮说"按区域"，第 3 轮说"还是刚才那个指标"
——模型能理解第 3 轮的"刚才那个指标"指的是 GMV

## 关键理解
- Without Memory: 每轮对话都是独立的，模型不知道上文
- With Memory: 每次 invoke 时，memory 自动把历史注入 Prompt
