import json
from app.agents.base_agent import BaseAgent
from app.models.trip import TripContext, ParsedIntent
from app.clients.ollama_client import OllamaClient

class IntentParserAgent(BaseAgent):
    """
    意图分析 Agent。
    职责：将用户的原始自然语言查询转换为结构化的 ParsedIntent 对象。
    """

    def __init__(self, ollama_client: OllamaClient, model_name: str):
        super().__init__(ollama_client, model_name)
        # 加载此 Agent 专用的 Prompt 模板
        self.prompt_template = self._load_prompt_template("intent_parser.txt")
        # 定义此 Agent 希望 AI 返回的 JSON 格式的系统提示
        self.system_message = (
            "You are an expert travel assistant. "
            "Your task is to extract structured information from the user's query. "
            "You MUST respond with a valid JSON object in the following format: "
            '{"destination": "string", "days": "integer", "budget": "string or null", "interests": ["list", "of", "strings"]}'
        )

    async def execute(self, context: TripContext) -> TripContext:
        """
        执行意图分析。
        """
        print("--- [Agent] 正在执行意图分析 ---")
        
        # 格式化 Prompt
        prompt = self.prompt_template.format(
            user_query=context.userInput.rawQuery
        )

        try:
            # 调用 Ollama API 获取结构化响应
            response_json = await self.ollama_client.get_structured_response(
                model_name=self.model_name,
                prompt=prompt,
                system_message=self.system_message
            )
            
            # 使用 Pydantic 模型验证和解析 JSON 响应
            # 这提供了强大的数据校验
            parsed_intent = ParsedIntent(**response_json)
            
            # 更新上下文
            context.parsedIntent = parsed_intent
            context.status = "intent_parsed"
            print(f"--- [Agent] 意图分析完成: {parsed_intent} ---")

        except Exception as e:
            print(f"--- [Agent] 意图分析失败: {e} ---")
            context.errorLog.append(f"IntentParserAgent 失败: {str(e)}")
            context.status = "error"
            
        return context
