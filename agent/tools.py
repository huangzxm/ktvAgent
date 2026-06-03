
"""
Agent 工具定义
包含 4 个工具:
1. search_device_guide - 搜索设备指南
2. search_songs - 搜索歌曲
3. query_sales_data - 查询销售数据
4. analyze_competitors - 竞品分析
"""

import os
import sys
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

# 添加上级目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vector_db.faiss_db import FAISSVectorDB, COLLECTION_NAMES

# 加载环境变量
load_dotenv()


class AgentTools:
    def __init__(self):
        self.vector_db = FAISSVectorDB()

    def search_device_guide(self, query: str, top_k: int = 3) -> Dict[str, Any]:
        """
        搜索设备指南，用于解答设备使用、安装、故障排查等问题
        :param query: 用户问题
        :param top_k: 返回结果数量
        :return: 搜索结果
        """
        results = self.vector_db.search(COLLECTION_NAMES["device"], query, top_k=top_k)
        
        context = "\n".join([
            f"【相关文档 {i+1}】\n{res['text']}\n"
            for i, res in enumerate(results)
        ])
        
        return {
            "tool": "search_device_guide",
            "query": query,
            "context": context,
            "results": results
        }

    def search_songs(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """
        搜索歌曲库，根据用户需求推荐合适的歌曲
        :param query: 用户需求描述（如：适合老人小孩唱的歌、练气息的歌）
        :param top_k: 返回结果数量
        :return: 搜索结果
        """
        results = self.vector_db.search(COLLECTION_NAMES["song"], query, top_k=top_k)
        
        context = "\n".join([
            f"【推荐歌曲 {i+1}】\n{res['text']}\n"
            for i, res in enumerate(results)
        ])
        
        return {
            "tool": "search_songs",
            "query": query,
            "context": context,
            "results": results
        }

    def query_sales_data(self, query: str, top_k: int = 3) -> Dict[str, Any]:
        """
        查询销售数据，包括区域出货、渠道表现、产品销售情况等
        :param query: 查询需求（如：华东区Q1出货、美视清系列销售）
        :param top_k: 返回结果数量
        :return: 搜索结果
        """
        results = self.vector_db.search(COLLECTION_NAMES["sales"], query, top_k=top_k)
        
        context = "\n".join([
            f"【销售数据 {i+1}】\n{res['text']}\n"
            for i, res in enumerate(results)
        ])
        
        return {
            "tool": "query_sales_data",
            "query": query,
            "context": context,
            "results": results
        }

    def analyze_competitors(self, query: str, top_k: int = 4) -> Dict[str, Any]:
        """
        竞品分析工具，查询竞品动态、优劣势对比等信息
        :param query: 分析需求（如：主要竞品有哪些、全民K歌优势劣势）
        :param top_k: 返回结果数量
        :return: 分析结果
        """
        # 优先搜索竞品相关内容
        enhanced_query = f"竞品分析 {query}"
        results = self.vector_db.search(COLLECTION_NAMES["sales"], enhanced_query, top_k=top_k)
        
        context = "\n".join([
            f"【竞品信息 {i+1}】\n{res['text']}\n"
            for i, res in enumerate(results)
        ])
        
        return {
            "tool": "analyze_competitors",
            "query": query,
            "context": context,
            "results": results
        }

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """
        获取工具定义，供 LLM 使用
        :return: 工具定义列表
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": "search_device_guide",
                    "description": "搜索设备知识库，解答设备安装、故障排查、功能使用等问题，适用于用户询问智能电视、机顶盒、智能音响、鸿蒙智慧屏等设备相关问题",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "用户的具体问题描述，如：'金运机顶盒黑屏怎么办'、'鸿蒙智慧屏怎么开启AI评分'"
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_songs",
                    "description": "搜索歌曲库，根据用户需求推荐合适的歌曲，可按场合、难度、风格、练唱目标等条件推荐",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "用户的歌曲需求描述，如：'适合老人小孩合唱的简单歌曲'、'适合练气息的流行女声'"
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "query_sales_data",
                    "description": "查询销售数据知识库，获取区域出货量、渠道商表现、产品销售情况等业务信息，适用于销售经理、渠道商等内部用户",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "业务查询需求，如：'华东区Q1智能音响出货量'、'美视清Pro退货率'"
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "analyze_competitors",
                    "description": "竞品分析工具，查询竞品动态、市场份额、优劣势对比等信息，辅助制定市场策略",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "竞品分析需求，如：'主要竞品有哪些'、'全民K歌和雷石对比'"
                            }
                        },
                        "required": ["query"]
                    }
                }
            }
        ]


# 单例模式
_tools_instance = None


def get_agent_tools() -> AgentTools:
    """获取 AgentTools 单例"""
    global _tools_instance
    if _tools_instance is None:
        _tools_instance = AgentTools()
    return _tools_instance


if __name__ == "__main__":
    # 测试工具
    print("=== Agent Tools 测试 ===")
    tools = get_agent_tools()
    
    print("\n1. 测试 search_device_guide...")
    result = tools.search_device_guide("金运机顶盒黑屏")
    print(f"工具返回: {len(result['results'])} 条结果")
    print(result['context'][:500] + "...")
    
    print("\n2. 测试 search_songs...")
    result = tools.search_songs("适合老人小孩唱的歌")
    print(f"工具返回: {len(result['results'])} 条结果")
    print(result['context'][:500] + "...")
    
    print("\n3. 测试 query_sales_data...")
    result = tools.query_sales_data("华东区Q1出货")
    print(f"工具返回: {len(result['results'])} 条结果")
    print(result['context'][:500] + "...")
    
    print("\n4. 测试 analyze_competitors...")
    result = tools.analyze_competitors("主要竞品")
    print(f"工具返回: {len(result['results'])} 条结果")
    print(result['context'][:500] + "...")
