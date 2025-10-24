# File: app/models/trip.py
from typing import Optional, List, Dict, Any
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
    poi_id: str = Field(description="来自地图服务或AI生成的唯一ID")
    name: str = Field(description="POI 名称")
    type: str = Field(description="POI 类型 (例如: attraction, dining, shopping)")
    # 更多POI详情可以根据需要添加...

class DailyItinerary(BaseModel):
    """
    每日行程的内嵌数据模型。
    """
    day_number: int = Field(..., description="行程第几天")
    theme: Optional[str] = Field(None, description="当天的主题，由AI生成")
    pois: List[PointOfInterest] = []

class BudgetBreakdown(BaseModel):
    """
    预算明细的内嵌数据模型。
    """
    transport: float = Field(0.0, description="交通费用")
    accommodation: float = Field(0.0, description="住宿费用")
    dining: float = Field(0.0, description="餐饮费用")
    activities: float = Field(0.0, description="活动/门票费用")
    other: float = Field(0.0, description="其他/购物费用")

class Budget(BaseModel):
    """
    预算总览的内嵌数据模型。
    """
    total_amount_str: str = Field(description="用户提供的原始总预算字符串")
    breakdown: Optional[BudgetBreakdown] = None

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
    
    daily_itineraries: List[DailyItinerary] = []
    budget: Optional[Budget] = None # (US003 新增)
    
    # 记录创建和更新时间
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "trip_plans"

# --- AI 多 Agent 工作流 (MCP) 模型 ---

class UserInput(BaseModel):
    """
    MCP: 用户的原始输入
    """
    rawQuery: str
    userProfile: Dict[str, Any]

class ParsedIntent(BaseModel):
    """
    MCP: 意图分析 Agent 的输出
    """
    destination: str
    days: int
    budget: Optional[str] = None
    interests: List[str] = []

class GeneratedFinalPlan(BaseModel):
    """
    MCP: 最终由 AI Agent 生成的计划结构
    """
    title: str
    daily_itineraries: List[DailyItinerary]
    budget: Optional[Budget] = None # (US003 新增)

class TripContext(BaseModel):
    """
    MCP: 行程上下文对象
    在多 Agent 工作流中传递的核心数据载体。
    """
    contextId: UUID = Field(default_factory=uuid4)
    status: str = Field(default="initialized")
    userInput: UserInput
    parsedIntent: Optional[ParsedIntent] = None
    # poiCandidates: Optional[List[PointOfInterest]] = None # (未来)
    finalPlan: GeneratedFinalPlan
    errorLog: List[str] = []

