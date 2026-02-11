from fastapi import APIRouter, Response

from db.database import DbSession
from schemas.auth import LoginResponse, UserInfoResponse
from schemas.login import LoginRequest
from schemas.response import BaseResponse
from services.auth import auth_service
from services.login import login_service

router = APIRouter()


@router.post(
    "",
    response_model=BaseResponse[LoginResponse],
    responses={404: {"model": BaseResponse}, 401: {"model": BaseResponse}},
)
def login(req: LoginRequest, db: DbSession, response: Response) -> BaseResponse[LoginResponse]:
    user = login_service.login(req, db)
    access_token, refresh_token = auth_service.create_tokens(user.id, db)

    response.headers["X-Refresh-Token"] = refresh_token
    login_response = LoginResponse(
        access_token=access_token,
        user=UserInfoResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            auth_provider=user.auth_provider,
        ),
    )
    return BaseResponse.ok(data=login_response, message="로그인 성공")
