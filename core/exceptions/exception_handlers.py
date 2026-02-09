from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from core.exceptions.base import CustomException
from core.exceptions.user import UserAlreadyExistsException, UserNotFoundException, UserPasswordNotMatchException
from schemas.response import BaseResponse


async def custom_base_handler(request: Request, exc: CustomException):
    content = BaseResponse.error(message=exc.message, code=exc.code).model_dump()
    return JSONResponse(
        status_code=exc.code,
        content=content,
    )


def init_exception_handlers(app: FastAPI):
    app.add_exception_handler(CustomException, custom_base_handler)
    app.add_exception_handler(UserNotFoundException, custom_base_handler)
    app.add_exception_handler(UserPasswordNotMatchException, custom_base_handler)
    app.add_exception_handler(UserAlreadyExistsException, custom_base_handler)
