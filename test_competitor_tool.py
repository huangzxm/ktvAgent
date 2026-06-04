
from agent.tools import get_agent_tools

# 测试新工具
print("=" * 60)
print("测试 compare_competitor_strategy 工具")
print("=" * 60)

tools = get_agent_tools()

# 测试例子
test_query = "全民K歌音响和我们雷石比，怎么抢他们的客户？"
print(f"\n用户问题：{test_query}")

result = tools.compare_competitor_strategy(test_query)
print("\n工具返回结果：")
print("-" * 60)
print(result["context"])

