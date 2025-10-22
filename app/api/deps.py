from typing import Annotated
from fastapi import Depends
from app.models.user import User

async def get_current_user_stub() -> User:
    """
    一个临时的依赖函数，用于在没有实现认证系统时提供一个模拟用户。
    在开发认证模块(FE002)时，这里将被替换为真正的Token验证逻辑。
    """
    # 尝试从数据库查找一个用户，如果不存在则创建一个
    mock_user = await User.find_one(User.email == "test@example.com")
    if not mock_user:
        mock_user = User(
            email="test@example.com",
            hashed_password="fake_password_hash", # 在实际应用中，这应该是经过哈希的密码
            nickname="测试用户"
        )
        await mock_user.insert()
    return mock_user

# 创建一个可以在API路由中使用的依赖项
CurrentUser = Annotated[User, Depends(get_current_user_stub)]