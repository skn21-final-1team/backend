from fastapi import APIRouter, Cookie, HTTPException, Response

from core.auth_guard import public
from core.config import get_settings
from db.database import DbSession
from schemas.auth import GoogleLoginRequest, LoginResponse, TokenResponse, UserInfoResponse
from schemas.response import BaseResponse
from services.auth import auth_service
from services.google_auth import google_auth_service

router = APIRouter()
settings = get_settings()


@router.post(
    "/google",
    response_model=BaseResponse[LoginResponse],
    responses={401: {"model": BaseResponse}, 409: {"model": BaseResponse}},
)
@public
def google_login(req: GoogleLoginRequest, db: DbSession, response: Response) -> BaseResponse[LoginResponse]:
    user = google_auth_service.verify_and_login(req.id_token, db)
    access_token, refresh_token = auth_service.create_tokens(user.id, db)

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60,
    )
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


@router.get(
    "/refresh",
    response_model=BaseResponse[TokenResponse],
    responses={401: {"model": BaseResponse}},
)
@public
def new_access_token(
    db: DbSession,
    response: Response,
    refresh_token: str | None = Cookie(default=None),
) -> BaseResponse[TokenResponse]:
    if refresh_token is None:
        raise HTTPException(status_code=403, detail="리프레시 토큰이 없습니다")
    new_access_token, new_refresh_token = auth_service.refresh_access_token(refresh_token, db)

    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60,
    )
    token_response = TokenResponse(access_token=new_access_token)
    return BaseResponse.ok(data=token_response, message="토큰 갱신 성공")
