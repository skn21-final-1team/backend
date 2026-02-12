from fastapi import APIRouter

from core.security import NotebookId
from db.database import DbSession
from schemas.extension import ExtensionBulkRequest
from schemas.response import BaseResponse
from services.extension import extension_service

router = APIRouter()


@router.post(
    "/bookmarks",
    response_model=BaseResponse[dict],
    responses={401: {"model": BaseResponse}, 403: {"model": BaseResponse}},
)
def bulk_import_bookmarks(
    req: ExtensionBulkRequest, db: DbSession, notebook_id: NotebookId
) -> BaseResponse[dict]:
    """
    확장 프로그램에서 북마크 뭉치를 받아서 저장합니다.
    - API Key(Notebook Key) 필수
    """
    extension_service.process_bulk_import(db, notebook_id, req.folders)
    return BaseResponse.ok({"message": "북마크 가져오기 성공"})
