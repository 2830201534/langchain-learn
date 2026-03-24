# LangGraph 进阶路径

> ⏱️ 学习周期：3天（2026-03-26 ~ 2026-03-28）
> 🎯 目标：掌握 LangGraph 状态机编排，理解它如何重构 codex 的决策链路

---

## 为什么学 LangGraph？

**LCEL 的局限**：管道式串联，无法做分支、循环、条件判断
**LangGraph 的能力**：有向有环图，支持 cycles（循环）、状态共享、人机交互

**对 codex 的价值：**

```
当前 codex：RouteDecision（硬编码四路 if-else）
LangGraph：状态机 → 每个节点可循环、可分支、可暂停等人类确认
```

---

## 三日计划

| 日期 | 主题 | 核心产出 |
|------|------|---------|
| 3/26 | LangGraph 基础：StateGraph / Node / Edge | 跑通最小状态机 |
| 3/27 | LangGraph 进阶：ConditionalEdge / Cycles / Checkpoint | 实现 SQL 重试循环 |
| 3/28 | 实战：用 LangGraph 重构 codex 决策链路 | 输出重构方案 |

---

## 目录结构

```
advanced/langgraph/
├── day1_240326/
│   ├── new_learning.md  # StateGraph / Node / Edge 基础
│   └── exercises.md      # 练习题
├── day2_240327/
│   ├── new_learning.md  # ConditionalEdge / Cycles / Checkpoint
│   └── exercises.md
└── day3_240328/
    └── new_learning.md  # 重构 codex 决策链路
```

---

## 学习环境

```bash
pip install langgraph langgraph-checkpoint
```

**注意：** `langgraph` 与 `langchain` 是两个独立包，LangGraph 不依赖 `langchain` 即可独立运行。
