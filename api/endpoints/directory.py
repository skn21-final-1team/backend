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
    responses={500: {"model": BaseResponse}},
)
def create_directory(
    req: DirectoryRequest, db: DbSession, user: CurrentUser
) -> BaseResponse[DirectoryResponse]:
    directory = directory_service.create_directory(req.notebook_id, req.title, req.parent_id, db)
    return BaseResponse.ok(DirectoryResponse.from_model(directory))


@router.get(
    "/",
    response_model=BaseResponse[list[DirectoryResponse]],
    responses={404: {"model": BaseResponse}},
)
def get_directories(
    notebook_id: int = Query(..., description="노트북 ID"),
    parent_id: int | None | str = Query("unset", description="부모 디렉토리 ID"),
    db: DbSession = None,
    user: CurrentUser = None,
) -> BaseResponse[list[DirectoryResponse]]:
    directories = directory_service.get_directories(notebook_id, parent_id, db)
    return BaseResponse.ok([DirectoryResponse.from_model(d) for d in directories])


@router.get(
    "/{directory_id}",
    response_model=BaseResponse[DirectoryResponse],
    responses={404: {"model": BaseResponse}},
)
def get_directory(directory_id: int, db: DbSession, user: CurrentUser) -> BaseResponse[DirectoryResponse]:
    directory = directory_service.get_directory(directory_id, db)
    return BaseResponse.ok(DirectoryResponse.from_model(directory))


@router.patch(
    "/{directory_id}",
    response_model=BaseResponse[DirectoryResponse],
    responses={404: {"model": BaseResponse}},
)
def update_directory(
    directory_id: int, req: DirectoryRequest, db: DbSession, user: CurrentUser
) -> BaseResponse[DirectoryResponse]:
    directory = directory_service.update_directory(directory_id, req.title, req.parent_id, db)
    return BaseResponse.ok(DirectoryResponse.from_model(directory))


@router.delete(
    "/{directory_id}",
    response_model=BaseResponse[DirectoryResponse],
    responses={404: {"model": BaseResponse}},
)
def delete_directory(
    directory_id: int, db: DbSession, user: CurrentUser
) -> BaseResponse[DirectoryResponse]:
    directory = directory_service.delete_directory(directory_id, db)
    return BaseResponse.ok(DirectoryResponse.from_model(directory))
