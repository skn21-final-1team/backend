from fastapi import APIRouter

from schemas.response import BaseResponse
from schemas.signup import SignupRequest
from services.signup import signup_service

router = APIRouter()


@router.post(
    "/",
    response_model=BaseResponse[None],
    responses={409: {"model": BaseResponse}},
)
def signup(request: SignupRequest) -> BaseResponse[None]:
    signup_service.signup(request)
    return BaseResponse.ok(message="Signup successful")
