from fastapi import APIRouter, Request
from schemas.extension import ExtensionSyncKeyResponse

from core.auth_guard import get_current_user
from db.database import DbSession
from schemas.directory import ExtensionSyncRequest
from schemas.response import BaseResponse
from services.directory_sync import directory_sync_service
from services.extension_sync_key import extension_sync_key_service

router = APIRouter()


@router.get(
    "/key",
    response_model=BaseResponse[ExtensionSyncKeyResponse],
    responses={404: {"model": BaseResponse}},
)
def create_extension_sync_key(req: Request, db: DbSession) -> BaseResponse[ExtensionSyncKeyResponse]:
    user = get_current_user(req)
    sync_key, expires_at = extension_sync_key_service.generate_sync_key(user.id, db)
    return BaseResponse.ok(ExtensionSyncKeyResponse(sync_key=sync_key, expires_at=expires_at.isoformat()))


@router.post(
    "/sync",
    response_model=BaseResponse[None],
)
def sync_directory_data(req: ExtensionSyncRequest, db: DbSession) -> BaseResponse[None]:
    """extension 에서 북마크 동기화 호출용"""
    directory_sync_service.sync_bookmarks(req.sync_key, req.bookmarks, db)
    return BaseResponse.ok(data=None)
