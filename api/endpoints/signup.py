from fastapi import APIRouter, HTTPException, status

from schemas.auth import SignupData, SignupRequest
from schemas.response import BaseResponse
from services.signup import signup_service

router = APIRouter()


@router.post("/", response_model=BaseResponse[SignupData])
def signup(signup_request: SignupRequest) -> BaseResponse[SignupData]:
    user = signup_service.signup(signup_request)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )
    return BaseResponse(
        code=200,
        message="Signup successful",
        data=SignupData(
            user_id=int(user["id"]),
            email=str(user["email"]),
            name=str(user["name"]),
        ),
    )
