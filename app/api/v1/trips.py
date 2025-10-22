from fastapi import APIRouter, status
from app.models.trip import TripGenerationRequest, TripPlan
from app.api.deps import CurrentUser
from app.services import trip_service

router = APIRouter()

@router.post(
    "/generate",
    response_model=TripPlan,
    status_code=status.HTTP_201_CREATED,
    summary="AI智能生成旅行计划"
)
async def generate_trip_plan(
    request: TripGenerationRequest,
    current_user: CurrentUser,
):
    """
    接收用户的旅行需求，并启动AI多Agent工作流来生成一份个性化的旅行计划。

    - **destination**: 目的地城市 (例如: "东京")
    - **days**: 旅行天数 (例如: 5)
    - **user_prompt**: 用户的详细需求 (例如: "我想去东京玩5天，预算8000元，喜欢动漫和美食，必去秋叶原")
    """
    # 调用服务层的业务逻辑
    new_plan = await trip_service.generate_trip_plan_from_user_request(
        request=request,
        current_user=current_user
    )
    return new_plan

