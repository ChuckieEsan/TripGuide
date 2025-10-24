import json
from app.agents.base_agent import BaseAgent
from app.models.trip import TripContext, Budget, BudgetBreakdown
from app.clients.ollama_client import OllamaClient

class BudgeterAgent(BaseAgent):
    """
    预算分配 Agent。
    职责：根据用户的总预算和已生成的行程，估算各项支出的明细。
    """

    def __init__(self, ollama_client: OllamaClient, model_name: str):
        super().__init__(ollama_client, model_name)
        self.prompt_template = self._load_prompt_template("budgeter.txt")
        # 定义此 Agent 希望 AI 返回的 JSON 格式的系统提示
        self.system_message = (
            "You are a meticulous travel budget analyst. "
            "Your task is to break down a total budget into key categories. "
            "You MUST respond with a valid JSON object in the following format: "
            '{"transport": 1000.0, "accommodation": 2000.0, "dining": 1500.0, "activities": 500.0, "other": 0.0}'
        )

    async def execute(self, context: TripContext) -> TripContext:
        """
        执行预算分配。
        """
        # 只有在前一步成功，并且用户提供了预算时才执行
        if (context.status != "scheduling_done" or 
            not context.parsedIntent or 
            not context.parsedIntent.budget):
            
            print("--- [Agent] 预算分配 Agent 跳过：未提供预算或行程未生成 ---")
            # 如果没有预算，也应将状态推进，以便工作流可以正常结束
            context.status = "budgeting_done" 
            return context

        print("--- [Agent] 正在执行预算分配 ---")

        # 将行程列表转换为 JSON 字符串，以便 AI 可以"看到"行程的详细程度
        itineraries_json = json.dumps(
            [it.model_dump() for it in context.finalPlan.daily_itineraries], 
            ensure_ascii=False,
            indent=2
        )

        prompt = self.prompt_template.format(
            total_budget=context.parsedIntent.budget,
            destination=context.parsedIntent.destination,
            days=context.parsedIntent.days,
            itineraries_json=itineraries_json
        )

        try:
            response_json = await self.ollama_client.get_structured_response(
                model_name=self.model_name,
                prompt=prompt,
                system_message=self.system_message
            )

            # 1. 解析 AI 返回的预算明细
            breakdown = BudgetBreakdown(**response_json)

            # 2. 创建完整的 Budget 对象
            new_budget = Budget(
                total_amount_str=context.parsedIntent.budget, # 存储用户原始预算字符串
                breakdown=breakdown
            )

            # 3. 更新上下文
            context.finalPlan.budget = new_budget
            context.status = "budgeting_done"
            print(f"--- [Agent] 预算分配完成 ---")

        except Exception as e:
            print(f"--- [Agent] 预算分配失败: {e} ---")
            context.errorLog.append(f"BudgeterAgent 失败: {str(e)}")
            context.status = "error" # 预算失败不应停止整个流程，但要记录错误
            # 即使预算失败，我们也标记为 "budgeting_done" 以便流程继续
            context.status = "budgeting_done"

        return context
