from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from core.exceptions.base import CustomException
from core.exceptions.user import UserAlreadyExistsException, UserNotFoundException, UserPasswordNotMatchException
from schemas.response import BaseResponse


def custom_base_handler(request: Request, exc: CustomException) -> JSONResponse:
    response = BaseResponse.error(exc.message, exc.code)
    return JSONResponse(
        status_code=exc.code,
        content=response.model_dump()
    )


def init_exception_handlers(app: FastAPI):
    app.add_exception_handler(CustomException, custom_base_handler)
    app.add_exception_handler(UserNotFoundException, custom_base_handler)
    app.add_exception_handler(UserPasswordNotMatchException, custom_base_handler)
    app.add_exception_handler(UserAlreadyExistsException, custom_base_handler)
