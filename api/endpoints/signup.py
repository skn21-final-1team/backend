from fastapi import APIRouter

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
def signup(request: SignupRequest, db: DbSession) -> BaseResponse[None]:
    signup_service.signup(request, db)
    return BaseResponse.ok(data=None, message="Signup successful")
