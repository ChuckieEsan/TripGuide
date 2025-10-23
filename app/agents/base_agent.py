import os
from abc import ABC, abstractmethod
from app.clients.ollama_client import OllamaClient
from app.models.trip import TripContext

# 获取当前文件所在的目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROMPTS_DIR = os.path.join(BASE_DIR, "prompts")

class BaseAgent(ABC):
    """
    所有 Agent 的抽象基类。
    定义了一个标准的执行接口和共享功能。
    """
    def __init__(self, ollama_client: OllamaClient, model_name: str):
        self.ollama_client = ollama_client
        self.model_name = model_name

    @abstractmethod
    async def execute(self, context: TripContext) -> TripContext:
        """
        每个 Agent 必须实现的核心执行方法。
        它接收一个 TripContext，对其进行修改，然后返回它。
        """
        pass

    def _load_prompt_template(self, template_name: str) -> str:
        """
        从 'prompts' 文件夹加载一个提示词模板文件。
        """
        try:
            template_path = os.path.join(PROMPTS_DIR, template_name)
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            print(f"错误: Prompt 模板文件未找到: {template_path}")
            raise
        except Exception as e:
            print(f"加载 Prompt 模板时出错: {e}")
            raise
