from fastapi import APIRouter, Request

from core.auth_guard import get_current_user
from db.database import DbSession
from schemas.directory import DirectoryKeyResponse
from schemas.response import BaseResponse
from services.directory_key import directory_key_service

router = APIRouter()


@router.get(
    "/key",
    response_model=BaseResponse[DirectoryKeyResponse],
    responses={404: {"model": BaseResponse}},
)
def create_bookmark_sync_key(req: Request, db: DbSession) -> BaseResponse[DirectoryKeyResponse]:
    user = get_current_user(req)
    bookmark_sync_key, expires_at = directory_key_service.generate_directory_key(user.id, db)
    return BaseResponse.ok(DirectoryKeyResponse(bookmark_sync_key=bookmark_sync_key, expires_at=expires_at))
