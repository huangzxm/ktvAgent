# 雷石家用 K 歌智能助手

## 项目概述

这是一个为雷石家用 K 歌设备生态打造的智能助手原型，集成 C 端用户互动和 B 端业务分析能力，通过 Agent 编排和 RAG 技术实现智能问答。

## 核心特性

### 支持场景
- **场景 A**: C 端设备使用帮助（设备安装、故障排查、功能说明）
- **场景 B**: C 端多模态设备问诊（支持图片输入）
- **场景 C**: C 端智能选歌与练唱推荐
- **场景 D**: B 端销售与渠道分析
- **场景 E**: C 端 + B 端复合任务

### 工具设计（4 个）

1. **search_device_guide** - 检索设备手册
   - 服务方向：C 端
   - 功能：从设备知识库中检索安装、排障、功能操作说明

2. **search_songs** - 智能歌曲推荐
   - 服务方向：C 端
   - 功能：根据难度、场合、风格、练唱目标推荐歌曲

3. **query_sales_data** - 查询销售数据
   - 服务方向：B 端
   - 功能：查询指定区域、机型、时间段的出货/销售数据

4. **analyze_competitors** - 竞品分析工具（自定义第 4 个工具）
   - 服务方向：B 端
   - 设计理由：在 KTV 和家用 K 歌市场竞争激烈的环境下，竞品分析对销售策略制定至关重要。该工具可快速检索竞品动态、优劣势对比、市场份额分析等信息，帮助渠道商和销售经理做出更明智的决策。

## 技术栈

- **语言**: Python
- **向量数据库**: Milvus Lite（轻量级，无需部署）
- **Embedding**: BAAI/bge-small-zh-v1.5（中文效果好，可本地运行）
- **LLM**: 智谱 AI（无需翻墙）
- **Web 框架**: FastAPI + Streamlit

## 快速开始

### 1. 安装依赖

```powershell
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并填写你的配置：

```powershell
Copy-Item .env.example .env
```

### 3. 准备数据并构建向量库

```powershell
# 先启动本地 Embedding 服务
python embeddings/bge_local_server.py

# 然后构建向量库
python milvus_db/milvus_lite.py --build
```

### 4. 运行前端

```powershell
streamlit run web/app.py
```

### 5. 运行测试

```powershell
python tests/test_scenarios.py
```

## 项目结构

```
lei_shi_karaoke_assistant/
├── README.md
├── .env.example
├── requirements.txt
├── data/
│   ├── device_manual.json      # 设备手册数据
│   ├── songs.json              # 歌曲库数据
│   └── sales_channel.json      # 销售渠道数据
├── embeddings/
│   └── bge_local_server.py     # BGE embedding 服务
├── milvus_db/
│   └── milvus_lite.py          # Milvus Lite 封装
├── agent/
│   ├── tools.py                # 4 个 Tool 实现
│   └── agent_loop.py           # Agent 主循环
├── web/
│   └── app.py                  # Streamlit 前端
└── tests/
    └── test_scenarios.py       # 场景 A-E 测试用例
```
