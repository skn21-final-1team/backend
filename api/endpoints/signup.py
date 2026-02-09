from fastapi import APIRouter, HTTPException, status

from schemas.response import BaseResponse
from services.signup import SignupRequest, signup_service

router = APIRouter()


@router.post("/", response_model=BaseResponse[None])
def signup(signup_request: SignupRequest) -> BaseResponse[None]:
    success = signup_service.signup(signup_request)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )
    return BaseResponse.ok(message="Signup successful")
