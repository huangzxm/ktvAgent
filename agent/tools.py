
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
        :param query: 用户问题（完整的用户问题）
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
        :param query: 用户需求描述（完整的用户问题，例如：适合老人小孩唱的歌）
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
        :param query: 查询需求（完整的用户问题，例如：华东区Q1智能音响出货、美视清Pro退货率）
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

    def compare_competitor_strategy(self, query: str, top_k: int = 4) -> Dict[str, Any]:
        """
        竞品对比与策略分析工具。不仅查询竞品信息，还结合自身产品优势，生成对比分析和应对策略。
        跨库联动：同时检索 sales_kb（竞品数据）和 device_kb（自身产品卖点）。
        
        :param query: 分析需求（完整的用户问题，例如：全民K歌音响和我们雷石比怎么抢他们的客户）
        :param top_k: 返回结果数量
        :return: 对比分析和应对策略
        """
        # 1. 从 sales_kb 检索竞品数据
        competitor_query = f"竞品分析 {query}"
        competitor_results = self.vector_db.search(COLLECTION_NAMES["sales"], competitor_query, top_k=top_k)
        
        # 2. 从 device_kb 检索自身产品功能卖点
        product_query = f"产品功能 卖点 {query}"
        product_results = self.vector_db.search(COLLECTION_NAMES["device"], product_query, top_k=top_k)
        
        # 3. 组合上下文
        competitor_context = "\n".join([
            f"【竞品信息 {i+1}】\n{res['text']}\n"
            for i, res in enumerate(competitor_results)
        ])
        
        product_context = "\n".join([
            f"【雷石产品卖点 {i+1}】\n{res['text']}\n"
            for i, res in enumerate(product_results)
        ])
        
        combined_context = f"""{competitor_context}

{product_context}
"""
        
        return {
            "tool": "compare_competitor_strategy",
            "query": query,
            "context": combined_context,
            "competitor_results": competitor_results,
            "product_results": product_results
        }

    def get_after_sales_trends(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """
        售后趋势分析工具。面向 B 端（销售经理、渠道商）的售后预警与质量评估检索器。
        从 sales_kb 中提取指定机型或区域的退货率、故障率、批量客诉记录及售后处理进度。
        
        :param query: 查询需求（完整的用户问题，例如：美视清Pro华南区退货率、最近有哪些批量客诉）
        :param top_k: 返回结果数量
        :return: 售后趋势数据
        """
        # 优先搜索售后、退货、客诉、故障相关内容
        enhanced_query = f"售后 退货率 客诉 故障率 {query}"
        results = self.vector_db.search(COLLECTION_NAMES["sales"], enhanced_query, top_k=top_k)
        
        context = "\n".join([
            f"【售后数据 {i+1}】\n{res['text']}\n"
            for i, res in enumerate(results)
        ])
        
        return {
            "tool": "get_after_sales_trends",
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
                    "description": "用于解答设备相关问题。当用户询问智能电视、机顶盒、智能音响、鸿蒙智慧屏等设备的安装、故障排查、功能使用时调用此工具。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "完整的用户问题，不要做任何修改，直接传入用户的原始问题"
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
                    "description": "用于推荐歌曲。当用户希望根据场合、难度、风格、练唱目标等条件推荐歌曲时调用此工具。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "完整的用户问题，不要做任何修改，直接传入用户的原始问题"
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
                    "description": "用于查询销售数据。当用户询问区域出货量、渠道表现、产品销售情况等业务数据时调用此工具。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "完整的用户问题，不要做任何修改，直接传入用户的原始问题"
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "compare_competitor_strategy",
                    "description": "用于竞品对比与策略分析。当用户询问竞品对比、如何抢竞品客户、产品差异化策略等问题时调用此工具。此工具会同时查询竞品信息和雷石自身产品卖点，提供跨库联动的业务决策支持。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "完整的用户问题，不要做任何修改，直接传入用户的原始问题"
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_after_sales_trends",
                    "description": "用于售后趋势分析。面向 B 端（销售经理、渠道商）的售后预警与质量评估工具。当用户询问退货率、故障率、批量客诉记录、售后处理进度等产品后端质量相关问题时调用此工具。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "完整的用户问题，不要做任何修改，直接传入用户的原始问题"
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
