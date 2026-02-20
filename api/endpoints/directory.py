from fastapi import APIRouter, Request

from core.auth_guard import get_current_user
from db.database import DbSession
from schemas.directory import DirectorySyncKeyRequest, DirectorySyncKeyResponse, DirectorySyncRequest
from schemas.response import BaseResponse
from services.directory_sync import directory_sync_service
from services.extension_sync_key import extension_sync_key_service

router = APIRouter()


@router.post(
    "/key",
    response_model=BaseResponse[DirectorySyncKeyResponse],
    responses={404: {"model": BaseResponse}},
)
def create_extension_sync_key(body: DirectorySyncKeyRequest, db: DbSession, request: Request):
    user = get_current_user(request)
    sync_key, expires_at = extension_sync_key_service.generate_sync_key(user.id, db, body.notebook_id)
    return BaseResponse.ok(DirectorySyncKeyResponse(sync_key=sync_key, expires_at=expires_at))


@router.post(
    "/sync",
    response_model=BaseResponse[None],
)
def sync_directory_data(body: DirectorySyncRequest, db: DbSession):
    """extension 에서 북마크 동기화 호출용"""
    directory_sync_service.sync_bookmarks(body.sync_key, body.bookmarks, db)
    return BaseResponse.ok(data=None)
