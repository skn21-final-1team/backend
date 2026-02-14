from fastapi import APIRouter

from core.auth_guard import public
from db.database import DbSession
from schemas.response import BaseResponse
from schemas.signup import SignupRequest
from services.signup import signup_service

router = APIRouter()


@router.post(
    "",
    response_model=BaseResponse[None],
    responses={409: {"model": BaseResponse}},
)
@public
def signup(request: SignupRequest, db: DbSession) -> BaseResponse[None]:
    signup_service.signup(request, db)
    return BaseResponse.ok(data=None, message="Signup successful")
