from fastapi import APIRouter

from core.auth_guard import get_current_user
from db.database import DbSession
from schemas.directory import DirectorySyncKeyRequest, DirectorySyncKeyResponse, DirectorySyncRequest
from schemas.response import BaseResponse
from services.directory_sync import directory_sync_service
from services.extension_sync_key import extension_sync_key_service

router = APIRouter()


@router.get(
    "/key",
    response_model=BaseResponse[DirectorySyncKeyResponse],
    responses={404: {"model": BaseResponse}},
)
def create_extension_sync_key(req: DirectorySyncKeyRequest, db: DbSession):
    user = get_current_user(req)
    sync_key, expires_at = extension_sync_key_service.generate_sync_key(user.id, db)
    return BaseResponse.ok(DirectorySyncKeyResponse(sync_key=sync_key, expires_at=expires_at))


@router.post(
    "/sync",
    response_model=BaseResponse[None],
)
def sync_directory_data(req: DirectorySyncRequest, db: DbSession):
    """extension 에서 북마크 동기화 호출용"""
    directory_sync_service.sync_bookmarks(req.sync_key, req.bookmarks, db)
    return BaseResponse.ok(data=None)
