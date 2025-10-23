from app.models.trip import TripGenerationRequest, TripPlan
from app.models.user import User
from datetime import datetime

# 导入 AI 协调器
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
            destination_city=request.destination, # 保持使用用户原始输入的目的地
            total_days=request.days,             # 保持使用用户原始输入的天数
            daily_itineraries=generated_plan.daily_itineraries,
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

