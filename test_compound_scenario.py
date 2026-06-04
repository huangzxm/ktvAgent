
"""
测试复合场景（场景 E）
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent.agent_loop import get_karaoke_agent

print("="*60)
print("测试复合问题 (场景 E)")
print("="*60)

query = "美视清蓝牙连接问题很多，帮我整理一下解决办法，顺便看看华南区这款产品的销售情况"

print(f"\n用户问题: {query}\n")

agent = get_karaoke_agent()
response = agent.chat(query)

print("-"*60)
print("助手回答:")
print(response)
