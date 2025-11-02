from fastapi import HTTPException, status
from beanie import PydanticObjectId
from typing import List
from app.models.trip import TripGenerationRequest, TripPlan
from app.models.user import User
from datetime import datetime

from app.agents.orchestrator import AIOrchestrator

async def generate_trip_plan_from_user_request(
    request: TripGenerationRequest,
    current_user: User
) -> TripPlan:
    """
    根据用户请求创建旅行计划的核心业务逻辑。
    [US002 更新]: 调用 AI Orchestrator 替换占位逻辑。
    """
    print(f"开始为用户 {current_user.email} 生成计划，目的地: {request.destination}")

    # 1. 实例化 AIOrchestrator
    orchestrator = AIOrchestrator()

    try:
        # 2. 调用协调器处理请求，它将返回一个结构化的行程数据
        generated_plan = await orchestrator.process_request(
            user_request=request,
            user=current_user
        )

        # 3. 将 AI 返回的结果映射到要存入数据库的 TripPlan 文档模型
        new_trip_plan = TripPlan(
            user=current_user,
            title=generated_plan.title,
            destination_city=request.destination, # S003 保持使用用户原始输入的目的地
            total_days=request.days,             # S003 保持使用用户原始输入的天数
            daily_itineraries=generated_plan.daily_itineraries,
            budget=generated_plan.budget, # (US003 新增)
            status="draft",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        # 4. 将新创建的计划存入数据库
        await new_trip_plan.insert()
        
        print(f"为用户 {current_user.email} 成功创建 AI 计划, ID: {new_trip_plan.id}")

        return new_trip_plan
    
    except Exception as e:
        print(f"AI 计划生成失败: {e}")
        # 在这里可以抛出一个 HTTP 异常，让 API 路由层捕获
        # (例如: raise HTTPException(status_code=500, detail=str(e)))
        # 为简单起见，我们暂时只打印错误并返回 None 或抛出异常
        raise

# --- (FE001 新增) ---

async def get_trip_plans_for_user(current_user: User) -> List[TripPlan]:
    """
    (US004) 获取当前用户的所有旅行计划列表
    """
    # Beanie 2.0.0 使用 Link.id 进行查询
    return await TripPlan.find(
        TripPlan.user.id == current_user.id
    ).to_list()

async def get_trip_plan_by_id(
    trip_id: PydanticObjectId, 
    current_user: User
) -> TripPlan:
    """
    (US005) 获取单个旅行计划详情。
    必须确保该计划属于当前用户。
    """
    # 1. 根据 ID 查找计划
    trip = await TripPlan.get(trip_id)
    
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="未找到该旅行计划"
        )
        
    # 2. 验证所有权
    # 在 Beanie 2.0 中, Link 需要在使用前 fetch
    await trip.fetch_link(TripPlan.user)
    
    if trip.user.id != current_user.id:
        # 如果用户试图访问不属于他们的计划，返回 404 (安全最佳实践)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="未找到该旅行计划"
        )
        
    return trip

async def delete_trip_plan_by_id(
    trip_id: PydanticObjectId, 
    current_user: User
) -> None:
    """
    (US006) 删除一个旅行计划。
    必须确保该计划属于当前用户。
    """
    # 重用 get_trip_plan_by_id 逻辑来执行权限检查
    # 如果找不到或不属于该用户，它将自动引发 404
    trip_to_delete = await get_trip_plan_by_id(trip_id, current_user)
    
    # 执行删除
    await trip_to_delete.delete()
    return

