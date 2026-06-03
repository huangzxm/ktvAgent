
"""
场景测试用例
覆盖场景 A-E：
A. C端设备使用帮助
B. C端多模态设备问诊
C. C端智能选歌推荐
D. B端销售数据分析
E. C端+B端复合任务
"""

import os
import sys
import json
from dotenv import load_dotenv

# 添加上级目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.agent_loop import get_karaoke_agent


def print_separator(title: str):
    """打印分隔符"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)


def test_scenario_a():
    """
    场景 A: C端设备使用帮助
    测试设备安装、故障排查、功能使用问题
    """
    print_separator("场景 A: C端设备使用帮助")
    
    agent = get_karaoke_agent()
    
    test_cases = [
        {
            "name": "机顶盒黑屏问题",
            "query": "我的金运机顶盒连上电视后画面是黑的，雷石K歌打不开",
            "description": "测试设备故障排查能力"
        },
        {
            "name": "鸿蒙智慧屏AI评分",
            "query": "鸿蒙智慧屏怎么开启AI评分功能？",
            "description": "测试功能使用指导能力"
        },
        {
            "name": "智能音响蓝牙连接",
            "query": "美视清智能音响怎么连手机蓝牙？",
            "description": "测试设备连接指导能力"
        }
    ]
    
    for case in test_cases:
        print(f"\n--- 测试: {case['name']} ---")
        print(f"描述: {case['description']}")
        print(f"用户: {case['query']}")
        
        try:
            response = agent.chat(case['query'])
            print(f"助手: {response}")
            print("✓ 测试通过")
        except Exception as e:
            print(f"✗ 测试失败: {e}")
        
        agent.reset_conversation()


def test_scenario_b():
    """
    场景 B: C端多模态设备问诊（模拟图片分析）
    测试结合图片描述的故障诊断
    """
    print_separator("场景 B: C端多模态设备问诊")
    
    agent = get_karaoke_agent()
    
    test_cases = [
        {
            "name": "模拟报错截图",
            "query": "我电视上显示错误代码E003，麦克风没声音，这是什么问题？",
            "description": "测试结合错误信息的诊断能力"
        },
        {
            "name": "模拟蓝牙连接失败界面",
            "query": "美视清音响蓝牙一直连不上，指示灯是红色闪烁，之前都是好的，突然就这样了",
            "description": "测试结合状态描述的诊断能力"
        }
    ]
    
    for case in test_cases:
        print(f"\n--- 测试: {case['name']} ---")
        print(f"描述: {case['description']}")
        print(f"用户: {case['query']}")
        
        try:
            response = agent.chat(case['query'])
            print(f"助手: {response}")
            print("✓ 测试通过")
        except Exception as e:
            print(f"✗ 测试失败: {e}")
        
        agent.reset_conversation()


def test_scenario_c():
    """
    场景 C: C端智能选歌推荐
    测试根据场合、难度、风格推荐歌曲
    """
    print_separator("场景 C: C端智能选歌推荐")
    
    agent = get_karaoke_agent()
    
    test_cases = [
        {
            "name": "家庭聚会歌曲",
            "query": "家里有老人和小孩，推荐几首适合全家合唱的简单歌曲",
            "description": "测试家庭场景推荐能力"
        },
        {
            "name": "练气息歌曲",
            "query": "我想练流行女声，有没有难度适中、适合练气息的歌？",
            "description": "测试练唱推荐能力"
        },
        {
            "name": "经典老歌",
            "query": "推荐一些适合父母辈唱的经典老歌",
            "description": "测试特定人群推荐能力"
        }
    ]
    
    for case in test_cases:
        print(f"\n--- 测试: {case['name']} ---")
        print(f"描述: {case['description']}")
        print(f"用户: {case['query']}")
        
        try:
            response = agent.chat(case['query'])
            print(f"助手: {response}")
            print("✓ 测试通过")
        except Exception as e:
            print(f"✗ 测试失败: {e}")
        
        agent.reset_conversation()


def test_scenario_d():
    """
    场景 D: B端销售数据分析
    测试区域出货、渠道表现、竞品分析等业务查询
    """
    print_separator("场景 D: B端销售数据分析")
    
    agent = get_karaoke_agent()
    
    test_cases = [
        {
            "name": "华东区Q1出货",
            "query": "华东区Q1智能音响出货量同比怎么样？",
            "description": "测试区域销售数据查询能力"
        },
        {
            "name": "西南区渠道覆盖",
            "query": "西南区的渠道商覆盖有哪些空白点？",
            "description": "测试渠道分析能力"
        },
        {
            "name": "竞品分析",
            "query": "主要竞品有哪些？各有什么优劣势？",
            "description": "测试竞品分析能力"
        }
    ]
    
    for case in test_cases:
        print(f"\n--- 测试: {case['name']} ---")
        print(f"描述: {case['description']}")
        print(f"用户: {case['query']}")
        
        try:
            response = agent.chat(case['query'])
            print(f"助手: {response}")
            print("✓ 测试通过")
        except Exception as e:
            print(f"✗ 测试失败: {e}")
        
        agent.reset_conversation()


def test_scenario_e():
    """
    场景 E: C端+B端复合任务
    测试同时调用多个工具的能力
    """
    print_separator("场景 E: C端+B端复合任务")
    
    agent = get_karaoke_agent()
    
    test_cases = [
        {
            "name": "美视清问题+销售",
            "query": "最近美视清蓝牙连接投诉比较多，帮我整理一下常见故障排查办法，顺便看看这款机型在华南区的当月出货趋势",
            "description": "测试同时调用设备和销售工具的能力"
        },
        {
            "name": "产品分析+竞品",
            "query": "金运机顶盒最近销量怎么样？主要竞品是什么情况？",
            "description": "测试同时调用销售和竞品分析工具的能力"
        }
    ]
    
    for case in test_cases:
        print(f"\n--- 测试: {case['name']} ---")
        print(f"描述: {case['description']}")
        print(f"用户: {case['query']}")
        
        try:
            response = agent.chat(case['query'])
            print(f"助手: {response}")
            print("✓ 测试通过")
        except Exception as e:
            print(f"✗ 测试失败: {e}")
        
        agent.reset_conversation()


def test_multiturn():
    """
    多轮对话测试
    """
    print_separator("多轮对话测试")
    
    agent = get_karaoke_agent()
    
    print("\n--- 多轮对话 1 ---")
    try:
        # 第一轮
        print("用户1: 推荐几首适合家庭聚会的歌")
        response1 = agent.chat("推荐几首适合家庭聚会的歌")
        print(f"助手1: {response1}")
        
        # 第二轮
        print("\n用户2: 其中有适合老人唱的吗？")
        response2 = agent.chat("其中有适合老人唱的吗？")
        print(f"助手2: {response2}")
        
        print("✓ 多轮对话测试通过")
    except Exception as e:
        print(f"✗ 多轮对话测试失败: {e}")


def main():
    """运行所有测试"""
    # 加载环境变量
    load_dotenv()
    
    # 检查 API Key
    if not os.getenv("ZHIPUAI_API_KEY"):
        print("错误: 请在 .env 文件中设置 ZHIPUAI_API_KEY")
        return
    
    print("🎤 雷石 K 歌智能助手 - 场景测试")
    print("="*80)
    
    # 运行测试
    test_scenario_a()
    test_scenario_b()
    test_scenario_c()
    test_scenario_d()
    test_scenario_e()
    test_multiturn()
    
    # 总结
    print("\n" + "="*80)
    print("所有测试完成！")
    print("="*80)


if __name__ == "__main__":
    main()
