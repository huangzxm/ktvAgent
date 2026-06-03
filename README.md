# 雷石家用 K 歌智能助手

## 项目概述

这是一个为雷石家用 K 歌设备生态打造的智能助手原型，集成 C 端用户互动和 B 端业务分析能力，通过 Agent 编排和 RAG 技术实现智能问答。

## 核心特性

### 支持场景
- **场景 A**: C 端设备使用帮助（设备安装、故障排查、功能说明）
- **场景 B**: C 端多模态设备问诊（支持图片上传分析）
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

4. **analyze_competitors** - 竞品分析工具
   - 服务方向：B 端
   - 设计理由：在 KTV 和家用 K 歌市场竞争激烈的环境下，竞品分析对销售策略制定至关重要。该工具可快速检索竞品动态、优劣势对比、市场份额分析等信息，帮助渠道商和销售经理做出更明智的决策。

## 技术栈

- **语言**: Python 3.8+
- **向量数据库**: 本地 FAISS（纯 Python 实现，无需额外依赖）
- **Embedding**: ModelScope（BGE 模型，国内平台）
- **LLM**: 智谱 AI GLM（无需翻墙）
- **Web 框架**: Streamlit
- **其他依赖**: numpy, python-dotenv, pillow 等

## 快速开始

### 方法一：一键启动（推荐）

使用 Python 启动脚本，自动完成所有配置：

```powershell
python setup_and_run.py
```

这个脚本会自动：
- 检查 Python 环境
- 配置智谱 AI API Key
- 安装项目依赖
- 构建向量知识库
- 启动 Web 应用

### 方法二：手动启动

#### 1. 安装依赖

```powershell
pip install -r requirements.txt
```

#### 2. 配置环境变量

复制 `.env.example` 为 `.env`：

```powershell
Copy-Item .env.example .env
```

然后编辑 `.env`，填入你的智谱 AI API Key：
```
ZHIPUAI_API_KEY=你的_API_Key
```

#### 3. 构建向量数据库

```powershell
python vector_db/faiss_db.py --build
```

#### 4. 启动应用

```powershell
streamlit run web/app.py
```

### 运行测试

```powershell
python tests/test_scenarios.py
```

## 项目结构

```
lei_shi_karaoke_assistant/
├── README.md                  # 项目说明文档
├── requirements.txt           # Python 依赖
├── setup_and_run.py           # 一键启动脚本
├── .env.example               # 环境变量模板
├── data/                      # 数据目录
│   ├── device_manual.json     # 设备手册数据
│   ├── songs.json             # 歌曲库数据
│   └── sales_channel.json     # 销售渠道数据
├── embeddings/                # 嵌入模型
│   └── bge_local_server.py    # BGE 本地向量服务
├── vector_db/                 # 向量数据库
│   └── faiss_db.py            # FAISS 向量数据库实现
├── agent/                     # Agent 模块
│   ├── tools.py               # 4 个工具实现
│   └── agent_loop.py          # Agent 主循环
├── web/                       # Web 应用
│   └── app.py                 # Streamlit 前端
└── tests/                     # 测试模块
    └── test_scenarios.py      # 场景 A-E 测试用例
```

## 使用说明

### 智谱 AI API Key 获取

1. 访问 https://open.bigmodel.cn
2. 注册并登录账号
3. 在控制台获取 API Key

### 向量数据库说明

- 数据存储在 `vector_db/faiss_db/` 目录
- 使用 JSON 格式持久化，无需数据库服务
- 首次运行时自动从 `data/` 目录构建向量库

## 常见问题

### 模型下载慢/失败

使用 ModelScope 加载 BGE 模型，如果网络问题，会自动降级到简单字符级向量，保证系统正常运行。

### 端口占用

Streamlit 默认使用 8501 端口，可通过 `--server.port` 指定其他端口：
```powershell
streamlit run web/app.py --server.port 8080
```

## 许可证

本项目仅供学习和演示使用。
