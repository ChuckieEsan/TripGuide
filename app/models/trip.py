from typing import Optional
from beanie import Document, Link
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID, uuid4

from app.models.user import User

# --- API 请求/响应模型 (Pydantic) ---

class TripGenerationRequest(BaseModel):
    """
    AI生成旅行计划的API请求体。
    """
    destination: str = Field(..., min_length=1, description="目的地城市")
    days: int = Field(..., gt=0, le=30, description="旅行天数")
    user_prompt: str = Field(..., description="用户的自然语言需求描述")

# --- 数据库文档模型 (Beanie) ---

class PointOfInterest(BaseModel):
    """
    兴趣点 (POI) 的内嵌数据模型。
    """
    poi_id: str = Field(description="来自地图服务的唯一ID")
    name: str = Field(description="POI 名称")
    type: str = Field(description="POI 类型 (例如: attraction, dining, shopping)")
    # 更多POI详情可以根据需要添加...

class DailyItinerary(BaseModel):
    """
    每日行程的内嵌数据模型。
    """
    day_number: int = Field(..., description="行程第几天")
    theme: Optional[str] = Field(None, description="当天的主题，由AI生成")
    pois: list[PointOfInterest] = []

class TripPlan(Document):
    """
    旅行计划主模型，将被存储在MongoDB中。
    """
    # 使用 Link 类型来创建对 User 文档的引用
    # 这将在后台创建一个数据库引用，而不是嵌入整个 User 对象
    user: Link[User]
    
    title: str = Field(description="旅行计划的标题")
    destination_city: str = Field(description="目的地城市")
    total_days: int = Field(description="总天数")
    status: str = Field(default="draft", description="计划状态 (draft, active, completed)")
    
    daily_itineraries: list[DailyItinerary] = []
    
    # 记录创建和更新时间
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "trip_plans"

