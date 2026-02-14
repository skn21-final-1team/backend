from fastapi import APIRouter, Response

from core.auth_guard import public
from db.database import DbSession
from schemas.auth import GoogleLoginRequest, LoginResponse, RefreshTokenRequest, TokenResponse, UserInfoResponse
from schemas.response import BaseResponse
from services.auth import auth_service
from services.google_auth import google_auth_service

router = APIRouter()


@router.post(
    "/google",
    response_model=BaseResponse[LoginResponse],
    responses={401: {"model": BaseResponse}, 409: {"model": BaseResponse}},
)
@public
def google_login(req: GoogleLoginRequest, db: DbSession, response: Response) -> BaseResponse[LoginResponse]:
    user = google_auth_service.verify_and_login(req.id_token, db)
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
    return BaseResponse.ok(data=login_response, message="Google 로그인 성공")


@router.post(
    "/refresh",
    response_model=BaseResponse[TokenResponse],
    responses={401: {"model": BaseResponse}},
)
@public
def refresh_token(req: RefreshTokenRequest, db: DbSession, response: Response) -> BaseResponse[TokenResponse]:
    new_access_token, new_refresh_token = auth_service.refresh_access_token(req.refresh_token, db)

    response.headers["X-Refresh-Token"] = new_refresh_token
    token_response = TokenResponse(access_token=new_access_token)
    return BaseResponse.ok(data=token_response, message="토큰 갱신 성공")
