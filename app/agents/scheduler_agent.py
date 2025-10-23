import json
from app.agents.base_agent import BaseAgent
from app.models.trip import TripContext, DailyItinerary, PointOfInterest, GeneratedFinalPlan
from app.clients.ollama_client import OllamaClient

class SchedulerAgent(BaseAgent):
    """
    行程规划 Agent。
    职责：根据结构化的意图，生成详细的每日行程计划。
    
    注意: 为了实现 US002，此 Agent 将同时负责 POI 推荐和行程排序。
    在未来的版本中 (FE003)，这可以被拆分为 POIRecommenderAgent 和 SchedulerAgent。
    """
    
    def __init__(self, ollama_client: OllamaClient, model_name: str):
        super().__init__(ollama_client, model_name)
        self.prompt_template = self._load_prompt_template("scheduler.txt")
        self.system_message = (
            "You are a world-class travel planner. "
            "Your task is to create a detailed daily itinerary based on the user's structured preferences. "
            "You MUST respond with a valid JSON object in the exact format: "
            '{"title": "Creative Trip Title", "daily_itineraries": [{"day_number": 1, "theme": "Day Theme", "pois": [{"poi_id": "poi_123", "name": "POI Name", "type": "attraction/dining/shopping"}]}]}'
        )

    async def execute(self, context: TripContext) -> TripContext:
        """
        执行行程规划。
        """
        if context.status != "intent_parsed" or not context.parsedIntent:
            print("--- [Agent] 行程规划 Agent 跳过：意图未分析 ---")
            return context

        print("--- [Agent] 正在执行行程规划 ---")
        
        # 格式化 Prompt
        prompt = self.prompt_template.format(
            destination=context.parsedIntent.destination,
            days=context.parsedIntent.days,
            budget=context.parsedIntent.budget,
            interests=", ".join(context.parsedIntent.interests),
            raw_query=context.userInput.rawQuery
        )

        try:
            response_json = await self.ollama_client.get_structured_response(
                model_name=self.model_name,
                prompt=prompt,
                system_message=self.system_message
            )

            # 使用 Pydantic 模型验证和解析 JSON 响应
            generated_plan = GeneratedFinalPlan(**response_json)
            
            # 更新上下文
            context.finalPlan = generated_plan
            context.status = "scheduling_done"
            print(f"--- [Agent] 行程规划完成: {generated_plan.title} ---")

        except Exception as e:
            print(f"--- [Agent] 行程规划失败: {e} ---")
            context.errorLog.append(f"SchedulerAgent 失败: {str(e)}")
            context.status = "error"
            
        return context
