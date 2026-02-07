from fastapi import APIRouter

from schemas.auth import SignupRequest, SignupResponse
from services.signup import signup_service

router = APIRouter()


@router.post("/", response_model=SignupResponse)
def signup(signup_request: SignupRequest) -> SignupResponse:
    return signup_service.signup(signup_request)
