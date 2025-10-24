from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    应用配置类，用于管理环境变量。
    """
    PROJECT_NAME: str = "AI Trip Planner"
    API_V1_STR: str = "/api/v1"

    # MongoDB 配置
    MONGO_URI: str = "mongodb://localhost:27017"
    MONGO_DB_NAME: str = "trip_planner_db"

    # Ollama 配置
    OLLAMA_HOST: str = "http://localhost:11434"
    
    # AI Agent 模型配置
    # 建议使用功能更强、遵循指令更好的模型
    INTENT_PARSER_MODEL: str = "llama3:8b" 
    SCHEDULER_MODEL: str = "llama3:8b"
    BUDGETER_MODEL: str = "llama3:8b" # (US003 新增)

    class Config:
        # Pydantic V2 class Config
        case_sensitive = True
        # .env.example 文件可以作为配置的模板
        env_file = ".env"
        env_file_encoding = 'utf-8'


# 创建一个全局可用的配置实例
settings = Settings()

