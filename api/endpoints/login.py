from fastapi import APIRouter

from schemas.auth import LoginRequest, LoginResponse
from services.login import login_service

router = APIRouter()


@router.post("", response_model=LoginResponse)
def login(login_request: LoginRequest) -> LoginResponse:
    return login_service.login(login_request)
