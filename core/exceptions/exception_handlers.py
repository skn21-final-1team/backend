from fastapi import FastAPI

from core.exceptions.base import CustomException
from core.exceptions.user import UserNotFoundException
from schemas.response import BaseResponse


def custom_base_handler(request, exc):
    return BaseResponse.error(exc.message, exc.code)


def init_exception_handlers(app: FastAPI):
    app.add_exception_handler(CustomException, custom_base_handler)
    app.add_exception_handler(UserNotFoundException, custom_base_handler)
