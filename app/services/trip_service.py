from app.models.trip import TripGenerationRequest, TripPlan
from app.models.user import User

# 导入AI协调器 (虽然现在还没实现它的逻辑)
# from app.agents.orchestrator import AIOrchestrator

async def generate_trip_plan_from_user_request(
    request: TripGenerationRequest,
    current_user: User
) -> TripPlan:
    """
    根据用户请求创建旅行计划的核心业务逻辑。

    Args:
        request: 来自API的用户输入。
        current_user: 当前登录的用户。

    Returns:
        新创建的旅行计划对象。
    """
    print(f"开始为用户 {current_user.email} 生成计划，目的地: {request.destination}")

    # --- TODO: US002 将在此处实现 ---
    # 1. 实例化 AIOrchestrator
    #    orchestrator = AIOrchestrator()
    # 2. 调用协调器处理请求，它将返回一个完整的、结构化的行程数据
    #    generated_plan_data = await orchestrator.process_request(
    #        raw_query=request.user_prompt,
    #        user_profile={"preferences": current_user.preferences}
    #    )
    # --------------------------------

    # --- US001 的临时占位逻辑 ---
    # 在AI逻辑实现前，我们先创建一个空的占位计划并存入数据库
    # 这样可以先打通整个API链路
    placeholder_title = f"{request.destination} {request.days}日游 (AI规划中...)"
    
    new_trip_plan = TripPlan(
        user=current_user,
        title=placeholder_title,
        destination_city=request.destination,
        total_days=request.days,
        daily_itineraries=[], # AI Agent的结果将填充这里
    )

    # 将新创建的计划存入数据库
    await new_trip_plan.insert()
    
    print(f"为用户 {current_user.email} 创建了占位计划，ID: {new_trip_plan.id}")

    return new_trip_plan

