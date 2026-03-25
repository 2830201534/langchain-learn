# Day 4: RAG（检索增强）

## 目标
掌握文档切分 → 向量入库 → 检索 → 生成 的完整 RAG 链路

## 任务清单
- [ ] 学会用 `RecursiveCharacterTextSplitter` 切分文档
- [ ] 跑通 FAISS 向量数据库的 `from_texts()` + `similarity_search()`
- [ ] 理解 `RetrievalQA` Chain：检索 → 构建 Context → 生成回答
- [ ] 完成练习：用 RAG 实现"基于 codex 指标定义的问答"

## 验收标准
导入 codex 的指标定义作为知识库，问"GMV 的口径是什么"，能正确回答
"是 SUM(pay_amount)，过滤条件是 status='paid'"

## 重要概念
这个就是 codex 里 `SemanticQueryCatalogSnapshot` 的 LangChain 版本
