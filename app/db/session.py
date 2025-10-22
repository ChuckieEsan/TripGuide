from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.core.config import settings
from app.models.user import User
from app.models.trip import TripPlan

async def init_db():
    """
    初始化数据库连接和 Beanie ODM。
    """
    # 创建一个异步的 MongoDB 客户端
    client = AsyncIOMotorClient(settings.MONGO_URI)

    # 初始化 Beanie，传入数据库实例和所有需要映射的文档模型
    # Beanie 会自动在 MongoDB 中为这些模型创建索引
    await init_beanie(
        database=client[settings.MONGO_DB_NAME],
        document_models=[
            User,
            TripPlan,
        ]
    )
    print("数据库初始化成功...")