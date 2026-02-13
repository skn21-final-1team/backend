from fastapi import APIRouter
from core.security import ExtensionToken, NotebookId
from db.database import DbSession
from schemas.extension import ExtensionUploadRequest
from schemas.response import BaseResponse
from services.extension import extension_service

router = APIRouter()

@router.post("/bookmarks", response_model=BaseResponse)
def upload_bookmarks(
    req: ExtensionUploadRequest,
    db: DbSession,
    notebook_id: NotebookId
) -> BaseResponse:
    extension_service.process_extension_data(notebook_id, req.bookmarks, db)
    return BaseResponse.ok(message="북마크 동기화 완료")