
from agent.agent_loop import get_karaoke_agent

# 测试完整 Agent
print("=" * 60)
print("测试 Agent 使用 compare_competitor_strategy")
print("=" * 60)

agent = get_karaoke_agent()

test_query = "全民K歌音响和我们雷石比，怎么抢他们的客户？"
print(f"\n用户问题：{test_query}")

print("\nAgent 正在思考...")
response = agent.chat(test_query)

print("\n" + "=" * 60)
print("Agent 回答：")
print("=" * 60)
print(response)

