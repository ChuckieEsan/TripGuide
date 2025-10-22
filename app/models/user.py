from typing import Optional
from beanie import Document
from pydantic import Field, EmailStr

class User(Document):
    """
    用户模型，代表一个用户账户。
    """
    # Beanie 会自动处理 _id 字段
    email: EmailStr = Field(..., unique=True)
    hashed_password: str = Field(...)
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    # 旅行偏好，用于AI个性化推荐
    preferences: list[str] = []

    class Settings:
        # MongoDB collection 的名称
        name = "users"

