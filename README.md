# **AI 旅游规划 App (AI Trip Planner)**

本项目是一个由 AI 驱动的次世代旅游规划工具。用户可以通过自然语言描述需求，后端的多 Agent 系统将自动生成包含详细路线、景点和预算的个性化旅行计划。

## **当前项目状态 (V0.1)**

我们已经完成了项目**最核心的 AI 引擎**的开发，包括：

* **US001**: 搭建了 FastAPI \+ MongoDB 的基础架构，打通了 API 请求链路。  
* **US002**: 实现了基于 Ollama 的多 Agent 协调器 (AIOrchestrator)，能够通过 IntentParserAgent 和 SchedulerAgent 链式处理，将自然语言转化为完整的每日行程。  
* **US003**: 扩展了 Agent 链，加入了 BudgeterAgent，实现了对 AI 生成行程的自动预算拆解。

目前，后端服务已具备接收用户请求并返回完整 AI 规划方案（行程 \+ 预算）的能力。

## **技术栈**

* **后端框架**: FastAPI  
* **数据库**: MongoDB (使用 Beanie 作为 ODM)  
* **AI 核心**: Ollama (通过 ollama-python 客户端调用)  
* **AI 编排**: 自定义多 Agent 协调器 (MCP 协议)  
* **环境与依赖**: Conda (管理 Python 解释器) \+ Poetry (管理项目依赖)

## **项目安装与启动**

### **1\. 环境准备**

本项目使用 Conda 管理 Python 环境，使用 Poetry 管理依赖。

\# 1\. 创建一个新的 Conda 环境 (推荐使用 Python 3.11)  
conda create \--name trip-planner-ai python=3.11

\# 2\. 激活环境  
conda activate trip-planner-ai

\# 3\. 在环境中安装 Poetry  
conda install \-c conda-forge poetry

### **2\. 安装依赖**

\# 1\. 克隆项目后，进入项目根目录 (trip-planner-ai/)  
\# 2\. 配置 Poetry 使用当前的 Conda 环境 (非常重要！)  
poetry config virtualenvs.create false \--local

\# 3\. 安装所有项目依赖  
poetry install

### **3\. 启动应用**

在启动 FastAPI 应用之前，请确保您的**MongoDB 服务**和 **Ollama 服务**已经启动并正在运行。

\# 1\. (可选) 确保 Ollama 拥有 Agent 所需的模型  
\# 我们在 app/core/config.py 中配置了 llama3:8b  
ollama pull llama3:8b

\# 2\. (可选) 确保 MongoDB 正在运行在 localhost:27017

\# 3\. 启动 FastAPI 服务器  
\# 确保您位于项目根目录 (pyproject.toml 所在的位置)  
uvicorn app.main:app \--reload

服务器成功启动后，您将在终端看到类似 Uvicorn running on http://127.0.0.1:8000 的提示。

您可以访问 [http://127.0.0.1:8000/docs](https://www.google.com/search?q=http://127.0.0.1:8000/docs) 查看并测试所有 API。

### **4\. 停止应用**

在运行 uvicorn 命令的终端中，按下 CTRL+C 即可停止服务器。

## **功能需求与开发优先级**

下表详细列出了本项目的功能特性 (FE) 和对应的用户故事 (US)。

| 优先级 | 需求 ID | 需求描述 | US ID | US 描述 | 对应模块 |
| :---- | :---- | :---- | :---- | :---- | :---- |
| **P0** | **FE001** | **核心用户认证** | US011 | 用户可以使用邮箱、密码注册新账号 | models.user, api.v1.users |
|  |  |  | US012 | 用户可以通过邮箱、密码登录，获取 JWT Token | api.v1.token, core.security |
| **P0** | **FE002** | **AI 核心规划流程** | **US001** | **(已完成)** 用户能通过 API 发起一次 AI 规划请求 | api.v1.trips, services.trip\_service |
|  |  |  | **US002** | **(已完成)** AI Agent 链式处理用户请求，生成每日行程 | agents.\*, clients.ollama\_client |
|  |  |  | **US003** | **(已完成)** AI Agent 自动为生成的行程分配预算明细 | agents.budgeter\_agent, models.trip |
|  |  |  | US004 | 用户可以获取自己创建的所有旅行计划列表 | api.v1.trips, services.trip\_service |
|  |  |  | US005 | 用户可以获取单个旅行计划的详细信息 | api.v1.trips, services.trip\_service |
|  |  |  | US006 | 用户可以删除一个旅行计划 | api.v1.trips, services.trip\_service |
| **P1** | **FE003** | **AI 规划质量优化** | US009 | (优化) 引入专职的 POI 推荐 Agent | agents.poi\_recommender |
|  |  |  | US010 | (优化) 引入地图/交通 Agent 优化路线合理性 | agents.map\_agent, clients.map\_client |
| **P1** | **FE004** | **人机协同编辑** | US007 | 用户可以修改旅行计划的基础信息（如标题） | api.v1.trips, services.trip\_service |
|  |  |  | US008 | 用户可以编辑每日行程（增/删/改 POI） | api.v1.trips, services.trip\_service |
| **P2** | **FE005** | **目的地探索** | \- | *待规划* | api.v1.destinations |
| **P2** | **FE006** | **计划导出与分享** | \- | *待规划* | services.export\_service |

