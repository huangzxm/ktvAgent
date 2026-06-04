
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

【绝对必须遵守的规则】
1. 对于复合问题（同时涉及多个方面），必须同时调用所有相关工具！绝对不能只调用其中一个！
   - 例如用户问："美视清蓝牙连接问题很多，帮我整理一下解决办法，顺便看看华南区这款产品的销售情况"
   - 必须同时调用两个工具：
     a) search_device_guide - 传入完整问题："美视清蓝牙连接问题很多，帮我整理一下解决办法，顺便看看华南区这款产品的销售情况"
     b) query_sales_data - 传入完整问题："美视清蓝牙连接问题很多，帮我整理一下解决办法，顺便看看华南区这款产品的销售情况"
   - 禁止只调用一个工具！

2. 每个工具都必须传入用户的完整原始问题，不要做任何修改或截断！

3. 工具调用后，要整合所有工具返回的信息，不要遗漏！

回答要求：
- 用简洁明了的语言回答
- 引用工具返回的信息时要自然
- 不同部分用清晰的标题或分段分开
- 确保包含所有工具的结果！
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
            "temperature": 0.5,
            "max_tokens": 3000
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
        
        # 检测复合问题 - 强制调用多个工具
        is_compound = False
        tools_to_call = []
        
        # 检测是否同时需要设备帮助和销售数据
        keywords_device = ["设备", "机顶盒", "音响", "智慧屏", "安装", "故障", "连接", "蓝牙", "黑屏"]
        keywords_sales = ["销售", "出货", "渠道", "数据", "华南", "华东", "华北", "Q1", "Q2", "美视清"]
        
        has_device = any(k in user_input for k in keywords_device)
        has_sales = any(k in user_input for k in keywords_sales)
        
        if has_device and has_sales:
            print("\n[调试: 检测到复合问题，强制调用两个工具！]")
            is_compound = True
            # 强制创建工具调用，不依赖 LLM 的判断
            import uuid
            tool1_id = str(uuid.uuid4())
            tool2_id = str(uuid.uuid4())
            
            # 调用 search_device_guide
            tools_to_call.append({
                "id": tool1_id,
                "function": {
                    "name": "search_device_guide",
                    "arguments": json.dumps({"query": user_input})
                }
            })
            
            # 调用 query_sales_data
            tools_to_call.append({
                "id": tool2_id,
                "function": {
                    "name": "query_sales_data",
                    "arguments": json.dumps({"query": user_input})
                }
            })
            
            # 创建一个模拟的 response
            class MockToolCall:
                def __init__(self, tool_dict):
                    self.id = tool_dict["id"]
                    self.function = type('', (), {})()
                    self.function.name = tool_dict["function"]["name"]
                    self.function.arguments = tool_dict["function"]["arguments"]
            
            class MockResponse:
                def __init__(self, tool_list):
                    self.content = "正在查询相关信息..."
                    self.tool_calls = [MockToolCall(t) for t in tool_list]
            
            response = MockResponse(tools_to_call)
        else:
            # 正常流程 - 让 LLM 决定调用哪些工具
            # 构建消息
            messages = [{"role": "system", "content": self.system_prompt}] + self.conversation_history
            # 调用 LLM
            response = self._call_llm(messages, use_tools=True)
        
        # 调试输出 - 查看最终调用的工具
        if response.tool_calls:
            print(f"\n[调试: 调用了 {len(response.tool_calls)} 个工具:")
            for i, tc in enumerate(response.tool_calls):
                print(f"  {i+1}. {tc.function.name}: {tc.function.arguments}")
        
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
            
            # 构建整合用的消息
            messages_with_tools = [{"role": "system", "content": self.system_prompt}] + self.conversation_history
            
            # 添加工具响应到消息
            for tool_resp in tool_responses:
                messages_with_tools.append(tool_resp)
                self.conversation_history.append(tool_resp)
            
            # 添加明确的整合提示
            integration_prompt = """请根据上面工具返回的信息，整合出一个完整的回答。要求：
1. 用自然流畅的语言组织
2. 不同部分用清晰的标题或分段分开
3. 确保包含所有工具返回的关键信息
4. 不要遗漏任何一个工具的结果！"""
            
            messages_with_tools.append({
                "role": "user",
                "content": integration_prompt
            })
            
            # 再次调用 LLM 整合结果
            final_response = self._call_llm(messages_with_tools, use_tools=False)
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
