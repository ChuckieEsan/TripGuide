import ollama
import json
from app.core.config import settings

class OllamaClient:
    """
    一个封装了 ollama-python 客户端的异步封装类，
    专用于获取结构化的 JSON 响应。
    """
    def __init__(self):
        # 初始化异步客户端
        self.client = ollama.AsyncClient(host=settings.OLLAMA_HOST)

    async def get_structured_response(
        self, 
        model_name: str, 
        prompt: str, 
        system_message: str
    ) -> dict | list:
        """
        调用 Ollama API 并强制其返回 JSON 格式的响应。

        Args:
            model_name: 要使用的 Ollama 模型 (例如: "llama3:8b")
            prompt: 用户的输入 prompt
            system_message: 指导 AI 行为的系统消息

        Returns:
            一个字典或列表，代表从AI返回的已解析的JSON。
        """
        try:
            response = await self.client.chat(
                model=model_name,
                messages=[
                    {'role': 'system', 'content': system_message},
                    {'role': 'user', 'content': prompt}
                ],
                format='json'  # 关键：强制 Ollama 返回 JSON 格式
            )
            
            content = response['message']['content']
            
            # Ollama (format='json') 有时会返回被三重反引号包裹的 JSON 字符串
            # 我们需要清理这种情况
            if content.startswith("```json"):
                content = content[7:-3].strip()
            
            # 解析 JSON 字符串为 Python 字典或列表
            return json.loads(content)

        except json.JSONDecodeError as e:
            print(f"Ollama JSON 解析失败: {e}")
            print(f"原始响应内容: {response.get('message', {}).get('content', '')}")
            raise ValueError("AI 未能返回有效的 JSON 响应。")
        except Exception as e:
            print(f"调用 Ollama 时发生错误: {e}")
            raise
