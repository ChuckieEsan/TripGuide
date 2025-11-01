import pytest
import pytest_asyncio
from unittest.mock import AsyncMock  # 用于模拟异步方法

from app.core.config import settings
from app.agents.intent_parser_agent import IntentParserAgent
from app.clients.ollama_client import OllamaClient
from app.models.trip import TripContext, UserInput, GeneratedFinalPlan, ParsedIntent
from app.models.user import User

# 标记此文件中所有测试都为 asyncio 模式
pytestmark = pytest.mark.asyncio


@pytest.fixture
def mock_ollama_client(mocker):
    """
    创建一个 OllamaClient 的模拟对象。
    我们使用 pytest-mock 提供的 'mocker' 夹具。
    """
    # 创建一个 OllamaClient 的模拟实例
    client = mocker.MagicMock(spec=OllamaClient)
    
    # 模拟 get_structured_response 方法
    # 我们将其指定为 AsyncMock，因为它是异步的
    client.get_structured_response = AsyncMock()
    return client


@pytest.fixture
def base_trip_context():
    """
    创建一个用于测试的基础 TripContext 对象。
    """
    # [FIX] 移除了 User(...) 实例化，因为它是一个 Beanie Document，
    # 在单元测试中不应被实例化，且在此处也未被使用。
    # user = User(email="test@example.com", hashed_password="mock_password") # <- 导致错误，已移除
    
    user_input = UserInput(
        rawQuery="去东京玩5天，预算8000，喜欢动漫",
        userProfile={"preferences": ["anime"]}
    )
    # finalPlan 必须初始化，否则 agent 无法写入
    final_plan = GeneratedFinalPlan(title="", daily_itineraries=[])
    
    context = TripContext(
        userInput=user_input,
        finalPlan=final_plan
    )
    context.status = "initialized"
    return context


async def test_intent_parser_agent_success(mock_ollama_client, base_trip_context):
    """
    测试: 意图分析 Agent 成功执行的情况。
    """
    # --- 1. 准备 (Arrange) ---
    
    # 定义我们期望 OllamaClient 返回的模拟数据
    mock_ai_response = {
        "destination": "东京",
        "days": 5,
        "budget": "8000",
        "interests": ["动漫"]
    }
    
    # 配置模拟客户端：当 get_structured_response 被调用时，返回我们的模拟数据
    mock_ollama_client.get_structured_response.return_value = mock_ai_response
    
    # 实例化 Agent，传入 *模拟* 的客户端
    agent = IntentParserAgent(
        ollama_client=mock_ollama_client,
        model_name=settings.INTENT_PARSER_MODEL
    )
    
    # --- 2. 执行 (Act) ---
    
    # 执行我们要测试的方法
    result_context = await agent.execute(base_trip_context)
    
    # --- 3. 断言 (Assert) ---
    
    # 检查状态是否被正确更新
    assert result_context.status == "intent_parsed"
    
    # 检查 parsedIntent 是否已填充
    assert result_context.parsedIntent is not None
    assert isinstance(result_context.parsedIntent, ParsedIntent)
    
    # 检查 AI 返回的数据是否被正确解析
    assert result_context.parsedIntent.destination == "东京"
    assert result_context.parsedIntent.days == 5
    assert result_context.parsedIntent.budget == "8000"
    assert result_context.parsedIntent.interests == ["动漫"]
    
    # 检查模拟客户端是否被正确调用
    mock_ollama_client.get_structured_response.assert_called_once()


async def test_intent_parser_agent_failure(mock_ollama_client, base_trip_context):
    """
    测试: 当 OllamaClient 调用失败时，Agent 能否正确处理异常。
    """
    # --- 1. 准备 (Arrange) ---
    
    # 配置模拟客户端：当 get_structured_response 被调用时，主动抛出一个异常
    mock_ollama_client.get_structured_response.side_effect = Exception("Ollama connection failed")
    
    agent = IntentParserAgent(
        ollama_client=mock_ollama_client,
        model_name=settings.INTENT_PARSER_MODEL
    )
    
    # --- 2. 执行 (Act) ---
    
    result_context = await agent.execute(base_trip_context)
    
    # --- 3. 断言 (Assert) ---
    
    # 检查状态是否被更新为 "error"
    assert result_context.status == "error"
    
    # 检查错误日志是否被记录
    assert len(result_context.errorLog) == 1
    assert "IntentParserAgent 失败" in result_context.errorLog[0]
    assert "Ollama connection failed" in result_context.errorLog[0]
    
    # 检查 parsedIntent 是否未被填充
    assert result_context.parsedIntent is None

