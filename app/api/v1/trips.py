from fastapi import APIRouter, status, Response
from typing import List
from beanie import PydanticObjectId
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

# --- (FE001 新增) ---

@router.get(
    "/",
    response_model=List[TripPlan],
    summary="US004: 获取当前用户的所有旅行计划"
)
async def get_all_trip_plans(
    current_user: CurrentUser,
):
    """
    获取登录用户创建的所有旅行计划列表。
    """
    return await trip_service.get_trip_plans_for_user(current_user)

@router.get(
    "/{trip_id}",
    response_model=TripPlan,
    summary="US005: 获取单个旅行计划详情"
)
async def get_trip_plan(
    trip_id: PydanticObjectId,
    current_user: CurrentUser,
):
    """
    根据 ID 获取单个旅行计划的详细信息。
    如果计划不存在或不属于当前用户，将返回 404。
    """
    return await trip_service.get_trip_plan_by_id(trip_id, current_user)

@router.delete(
    "/{trip_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="US006: 删除一个旅行计划"
)
async def delete_trip_plan(
    trip_id: PydanticObjectId,
    current_user: CurrentUser,
):
    """
    根据 ID 删除一个旅行计划。
    如果计划不存在或不属于当前用户，将返回 404。
    成功删除后，返回 204 No Content。
    """
    await trip_service.delete_trip_plan_by_id(trip_id, current_user)
    # 返回一个没有内容的 204 响应
    return Response(status_code=status.HTTP_204_NO_CONTENT)

