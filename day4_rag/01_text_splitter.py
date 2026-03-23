"""
Day 4 练习 1：文档切分
使用 RecursiveCharacterTextSplitter 将长文档切成小块
"""

from langchain.text_splitter import RecursiveCharacterTextSplitter

# 示例长文档
document = """
# 指标定义文档

## GMV（成交总额）
定义：所有已支付订单的支付金额总和
计算公式：SUM(pay_amount)
过滤条件：status = 'paid'
时间范围：按 created_at 统计

## 订单数量
定义：所有订单的总数量
计算公式：COUNT(id)
过滤条件：无
时间范围：按 created_at 统计

## 用户数量
定义：去重后的用户数
计算公式：COUNT(DISTINCT user_id)
过滤条件：无
时间范围：按 created_at 统计

## 客单价
定义：平均每单金额
计算公式：SUM(pay_amount) / COUNT(id)
过滤条件：status = 'paid'
"""

# 创建切分器
splitter = RecursiveCharacterTextSplitter(
    chunk_size=100,      # 每个 chunk 最大 100 字符
    chunk_overlap=20,     # 相邻 chunk 重叠 20 字符
    separators=["\n## ", "\n", "。", "，"]  # 分割符优先级
)

# 切分文档
chunks = splitter.split_text(document)

print(f"=== 文档切分结果（共 {len(chunks)} 个 chunk）===\n")
for i, chunk in enumerate(chunks, 1):
    print(f"Chunk {i}: {chunk}")
    print("-" * 50)
