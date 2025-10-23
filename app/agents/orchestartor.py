from app.clients.ollama_client import OllamaClient
from app.agents.intent_parser_agent import IntentParserAgent
from app.agents.scheduler_agent import SchedulerAgent
from app.models.trip import TripContext, TripGenerationRequest, GeneratedFinalPlan, UserInput
from app.models.user import User
from app.core.config import settings

class AIOrchestrator:
    """
    AI 协调器 (Orchestrator)。
    负责管理多 Agent 工作流 (MCP 协议) 的执行。
    """
    
    def __init__(self):
        # 1. 初始化 Ollama 客户端
        self.ollama_client = OllamaClient()
        
        # 2. 按顺序初始化并注册所有 Agent
        self.agents = [
            IntentParserAgent(
                self.ollama_client, 
                model_name=settings.INTENT_PARSER_MODEL
            ),
            SchedulerAgent(
                self.ollama_client,
                model_name=settings.SCHEDULER_MODEL
            ),
            # 未来的 Agent (如 BudgeterAgent) 可以在这里添加
        ]

    async def process_request(
        self,
        user_request: TripGenerationRequest,
        user: User
    ) -> GeneratedFinalPlan:
        """
        处理 AI 规划请求的主入口点。
        
        Args:
            user_request: 来自 API 的原始请求数据。
            user: 当前用户对象。
        
        Returns:
            一个包含标题和每日行程的 GeneratedFinalPlan 对象。
        
        Raises:
            Exception: 如果 AI 工作流中任何一步失败。
        """
        print("--- [Orchestrator] 开始处理 AI 请求 ---")
        
        # 1. [START] 创建初始的 Trip Context
        context = TripContext(
            userInput=UserInput(
                rawQuery=user_request.user_prompt,
                userProfile={"preferences": user.preferences}
            ),
            # 预先填充一些已知信息
            finalPlan=GeneratedFinalPlan(
                title=f"{user_request.destination} 之旅",
                daily_itineraries=[]
            )
        )
        
        # 2. 依次执行 Agent 链
        for agent in self.agents:
            if context.status == "error":
                print(f"--- [Orchestrator] 工作流因错误而提前终止 ---")
                break
            
            context = await agent.execute(context)
            
        # 3. 检查最终状态
        if context.status == "error" or not context.finalPlan.daily_itineraries:
            print(f"--- [Orchestrator] AI 工作流未能成功生成计划 ---")
            print(f"错误日志: {context.errorLog}")
            raise Exception(f"AI 工作流失败: {context.errorLog}")
            
        print("--- [Orchestrator] AI 请求处理成功 ---")
        
        # 4. 返回最终的规划结果
        return context.finalPlan
