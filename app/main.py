from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.config import settings
from app.db.session import init_db
from app.api.v1 import trips

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 在应用启动时执行
    print("应用启动...")
    await init_db()
    yield
    # 在应用关闭时执行
    print("应用关闭...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan,
    # 可以在这里添加其他元数据
    # version="1.0.0",
    # description="一个由AI驱动的次世代旅游规划工具",
)

# 包含v1版本的API路由
# 所有来自 trips.router 的路由都会自动加上 /api/v1/trips 的前缀
app.include_router(trips.router, prefix=f"{settings.API_V1_STR}/trips", tags=["Trips"])

@app.get("/", summary="健康检查")
def read_root():
    """
    根路径，用于简单的健康检查。
    """
    return {"status": "ok", "message": f"Welcome to {settings.PROJECT_NAME}"}

