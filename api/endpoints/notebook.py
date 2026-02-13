from fastapi import APIRouter

from core.security import CurrentUser, create_extension_token
from db.database import DbSession
from schemas.notebook import ExtensionTokenResponse, NotebookRequest, NotebookResponse
from schemas.response import BaseResponse
from services.notebook import notebook_service

router = APIRouter()


@router.post(
    "/",
    response_model=BaseResponse[NotebookResponse],
    responses={500: {"model": BaseResponse}},
)
def create_notebook(req: NotebookRequest, db: DbSession, user: CurrentUser) -> BaseResponse[NotebookResponse]:
    return BaseResponse.ok(notebook_service.create_notebook(user.id, req.title, db))


@router.post(
    "/{notebook_id}/extension-token",
    response_model=BaseResponse[ExtensionTokenResponse],
    responses={404: {"model": BaseResponse}, 403: {"model": BaseResponse}},
)
def generate_extension_token(notebook_id: int, db: DbSession, user: CurrentUser) -> BaseResponse[ExtensionTokenResponse]:
    notebook = notebook_service.get_notebook(notebook_id, db)
    
    if notebook.user_id != user.id:
         return BaseResponse.error(message="권한이 없습니다.", code=403)

    token = create_extension_token(notebook_id, user.id)
    return BaseResponse.ok(ExtensionTokenResponse(token=token))


@router.get(
    "/",
    response_model=BaseResponse[list[NotebookResponse]],
    responses={404: {"model": BaseResponse}},
)
def get_notebooks(db: DbSession, user: CurrentUser) -> BaseResponse[list[NotebookResponse]]:
    return BaseResponse.ok(notebook_service.get_notebooks_by_user(user.id, db))


@router.get(
    "/{notebook_id}",
    response_model=BaseResponse[NotebookResponse],
    responses={404: {"model": BaseResponse}},
)
def get_notebook(notebook_id: int, db: DbSession) -> BaseResponse[NotebookResponse]:
    return BaseResponse.ok(notebook_service.get_notebook(notebook_id, db))


@router.patch(
    "/{notebook_id}",
    response_model=BaseResponse[NotebookResponse],
    responses={404: {"model": BaseResponse}},
)
def update_notebook(notebook_id: int, req: NotebookRequest, db: DbSession) -> BaseResponse[NotebookResponse]:
    return BaseResponse.ok(notebook_service.update_notebook_title(notebook_id, req.title, db))


@router.delete(
    "/{notebook_id}",
    response_model=BaseResponse[NotebookResponse],
    responses={404: {"model": BaseResponse}},
)
def delete_notebook(notebook_id: int, db: DbSession) -> BaseResponse[NotebookResponse]:
    return BaseResponse.ok(notebook_service.delete_notebook(notebook_id, db))
