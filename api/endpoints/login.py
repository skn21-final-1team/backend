from fastapi import APIRouter

from schemas.login import LoginRequest, UserInfo
from schemas.response import BaseResponse
from services.login import login_service

router = APIRouter()


@router.post(
    "/",
    response_model=BaseResponse[UserInfo],
    responses={404: {"model": BaseResponse}, 401: {"model": BaseResponse}},
)
def login(req: LoginRequest) -> BaseResponse[UserInfo]:
    return BaseResponse.ok(login_service.login(req))
