"""
JWT 토큰 검증 테스트용 예시 엔드포인트

- 이 파일은 보호된 엔드포인트(Protected Endpoint) 구현 예시입니다.
- 현재 프로젝트에서 마이페이지 기능은 예정되어 있지 않아 실제 사용되지 않습니다.
- JWT 토큰 검증이 필요한 API 구현 시 참고용으로 활용하세요.
"""

from fastapi import APIRouter, Depends

from core.security import get_current_user
from schemas.auth import UserResponse

router = APIRouter()


@router.get("/me", response_model=UserResponse)
def get_my_info(current_user: dict[str, str | int] = Depends(get_current_user)) -> UserResponse:
    """
    내 정보 조회 (JWT 토큰 필수)

    - Authorization 헤더에 Bearer 토큰을 포함해야 접근 가능
    - 토큰이 없거나 만료된 경우 401 에러 반환
    """
    return UserResponse(
        user_id=int(current_user["id"]),
        email=str(current_user["email"]),
        name=str(current_user["name"]),
    )
