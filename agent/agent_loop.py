
"""
Agent 主循环
实现多轮对话、意图识别、工具调用、结果整合
使用智谱 AI (Zhipu AI) 作为 LLM
"""

import os
import sys
import json
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# 添加上级目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.tools import get_agent_tools
from zhipuai import ZhipuAI

# 加载环境变量
load_dotenv()

# 初始化智谱 AI 客户端
ZHIPU_API_KEY = os.getenv("ZHIPUAI_API_KEY")
if not ZHIPU_API_KEY:
    raise ValueError("请在 .env 文件中设置 ZHIPUAI_API_KEY")

client = ZhipuAI(api_key=ZHIPU_API_KEY)


class KaraokeAssistantAgent:
    def __init__(self):
        self.tools = get_agent_tools()
        self.conversation_history: List[Dict[str, Any]] = []
        self.system_prompt = """你是雷石家用 K 歌智能助手，能够帮助用户解决以下问题：

1. 设备使用帮助：解答智能电视、机顶盒、智能音响、鸿蒙智慧屏等设备的安装、故障排查、功能使用问题
2. 智能选歌推荐：根据用户的场合、难度、风格、练唱目标等需求推荐合适的歌曲
3. 销售数据分析：为内部销售经理、渠道商提供区域出货、渠道表现、产品销售等业务数据查询
4. 竞品分析：提供竞品动态、优劣势对比等市场分析信息

你可以根据用户问题自主判断调用哪些工具，也可以同时调用多个工具来解答复杂问题。

回答要求：
- 用简洁明了的语言回答
- 引用工具返回的信息时要自然
- 对于 C 端用户，语气友好、有帮助
- 对于 B 端用户，语气专业、数据准确
- 如果问题超出知识范围，诚实地告诉用户

注意：
- 当用户同时询问设备问题和销售数据时，需要调用多个工具
- 优先使用工具获取信息，不要编造内容
"""

    def reset_conversation(self):
        """重置对话历史"""
        self.conversation_history = []

    def _call_llm(self, messages: List[Dict[str, Any]], use_tools: bool = True) -> Dict[str, Any]:
        """
        调用 LLM
        :param messages: 消息列表
        :param use_tools: 是否使用工具
        :return: LLM 响应
        """
        params = {
            "model": "GLM-4-Flash",
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        if use_tools:
            params["tools"] = self.tools.get_tool_definitions()
            params["tool_choice"] = "auto"
        
        response = client.chat.completions.create(**params)
        return response.choices[0].message

    def _execute_tools(self, tool_calls: List[Any]) -> List[Dict[str, Any]]:
        """
        执行工具调用
        :param tool_calls: 工具调用列表
        :return: 工具执行结果列表
        """
        tool_responses = []
        
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            try:
                if function_name == "search_device_guide":
                    result = self.tools.search_device_guide(**function_args)
                elif function_name == "search_songs":
                    result = self.tools.search_songs(**function_args)
                elif function_name == "query_sales_data":
                    result = self.tools.query_sales_data(**function_args)
                elif function_name == "analyze_competitors":
                    result = self.tools.analyze_competitors(**function_args)
                else:
                    result = {"error": f"Unknown tool: {function_name}"}
                
                tool_responses.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": json.dumps(result, ensure_ascii=False)
                })
            except Exception as e:
                tool_responses.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": json.dumps({"error": str(e)}, ensure_ascii=False)
                })
        
        return tool_responses

    def chat(self, user_input: str) -> str:
        """
        处理用户输入并返回响应
        :param user_input: 用户输入
        :return: 助手响应
        """
        # 添加用户消息到历史
        self.conversation_history.append({
            "role": "user",
            "content": user_input
        })
        
        # 构建消息
        messages = [{"role": "system", "content": self.system_prompt}] + self.conversation_history
        
        # 第一次调用 LLM，可能会触发工具调用
        response = self._call_llm(messages, use_tools=True)
        
        # 如果有工具调用，则执行工具并再次调用 LLM
        if response.tool_calls:
            # 添加助手响应到历史
            self.conversation_history.append({
                "role": "assistant",
                "content": response.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in response.tool_calls
                ]
            })
            
            # 执行工具
            tool_responses = self._execute_tools(response.tool_calls)
            
            # 添加工具响应到历史和消息
            for tool_resp in tool_responses:
                self.conversation_history.append(tool_resp)
                messages.append(tool_resp)
            
            # 再次调用 LLM 整合结果
            final_response = self._call_llm(messages, use_tools=False)
        else:
            final_response = response
        
        # 添加最终响应到历史
        self.conversation_history.append({
            "role": "assistant",
            "content": final_response.content
        })
        
        return final_response.content


# 单例模式
_agent_instance = None


def get_karaoke_agent() -> KaraokeAssistantAgent:
    """获取 Agent 单例"""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = KaraokeAssistantAgent()
    return _agent_instance


if __name__ == "__main__":
    # 测试 Agent
    print("=== 雷石 K 歌智能助手测试 ===")
    agent = get_karaoke_agent()
    
    test_queries = [
        "我的金运机顶盒黑屏了，怎么办？",
        "推荐几首适合老人小孩合唱的歌",
        "华东区Q1智能音响出货量怎么样？",
        "美视清蓝牙连接问题很多，帮我整理一下解决办法，顺便看看华南区这款产品的销售情况"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*60}")
        print(f"测试 {i}: {query}")
        print('-'*60)
        response = agent.chat(query)
        print(f"助手: {response}")
        agent.reset_conversation()
