from fastapi import APIRouter, Query

from core.security import CurrentUser
from db.database import DbSession
from schemas.directory import DirectoryRequest, DirectoryResponse
from schemas.response import BaseResponse
from services.directory import directory_service

router = APIRouter()


@router.post(
    "/",
    response_model=BaseResponse[DirectoryResponse],
    responses={404: {"model": BaseResponse}, 401: {"model": BaseResponse}},
)
def create_directory(
    req: DirectoryRequest, notebook_id: int, db: DbSession, user: CurrentUser
) -> BaseResponse[DirectoryResponse]:
    return BaseResponse.ok(directory_service.create_directory(notebook_id, req.title, req.parent_id, db))


@router.get(
    "/notebook/{notebook_id}",
    response_model=BaseResponse[list[DirectoryResponse]],
    responses={404: {"model": BaseResponse}},
)
def get_directories_by_notebook(
    notebook_id: int, db: DbSession, user: CurrentUser
) -> BaseResponse[list[DirectoryResponse]]:
    return BaseResponse.ok(directory_service.get_directories_by_notebook(notebook_id, db))


@router.get(
    "/",
    response_model=BaseResponse[list[DirectoryResponse]],
    responses={404: {"model": BaseResponse}},
)
def get_directories_by_parent(
    db: DbSession,
    user: CurrentUser,
    notebook_id: int = Query(...),
    parent_id: int | None = Query(None),
) -> BaseResponse[list[DirectoryResponse]]:
    return BaseResponse.ok(directory_service.get_directories_by_parent(parent_id, notebook_id, db))


@router.get(
    "/{directory_id}",
    response_model=BaseResponse[DirectoryResponse],
    responses={404: {"model": BaseResponse}},
)
def get_directory(directory_id: int, db: DbSession, user: CurrentUser) -> BaseResponse[DirectoryResponse]:
    return BaseResponse.ok(directory_service.get_directory(directory_id, db))


@router.patch(
    "/{directory_id}",
    response_model=BaseResponse[DirectoryResponse],
    responses={404: {"model": BaseResponse}},
)
def update_directory(
    directory_id: int, req: DirectoryRequest, db: DbSession, user: CurrentUser
) -> BaseResponse[DirectoryResponse]:
    return BaseResponse.ok(directory_service.update_directory_title(directory_id, req.title, db))


@router.delete(
    "/{directory_id}",
    response_model=BaseResponse[DirectoryResponse],
    responses={404: {"model": BaseResponse}},
)
def delete_directory(directory_id: int, db: DbSession, user: CurrentUser) -> BaseResponse[DirectoryResponse]:
    return BaseResponse.ok(directory_service.delete_directory(directory_id, db))
