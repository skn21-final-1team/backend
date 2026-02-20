from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from core.exceptions.auth import (
    ExpiredRefreshTokenException,
    GoogleClientIdMismatchException,
    InvalidGoogleTokenException,
    InvalidRefreshTokenException,
    InvalidTokenException,
    OAuthAccountConflictException,
)
from core.exceptions.base import CustomException
from core.exceptions.chat import ChatNotFoundException
from core.exceptions.common import InvalidRequestException
from core.exceptions.crawl import CrawlFailedException, FirecrawlConnectionException, FirecrawlContainerException
from core.exceptions.notebook import NotebookNotFoundException
from core.exceptions.user import (
    InvalidUserException,
    UserAlreadyExistsException,
    UserNotFoundException,
    UserPasswordNotMatchException,
)
from schemas.response import BaseResponse


def custom_base_handler(_: Request, exc: CustomException) -> JSONResponse:
    response = BaseResponse.error(message=exc.message, code=exc.code)
    return JSONResponse(status_code=exc.code, content=response.model_dump())


def validation_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    errors = exc.errors()
    messages = [f"{'.'.join(str(loc) for loc in e['loc'])}: {e['msg']}" for e in errors]
    response = BaseResponse.error(message="; ".join(messages), code=422)
    return JSONResponse(status_code=422, content=response.model_dump())


def init_exception_handlers(app: FastAPI):
    app.add_exception_handler(RequestValidationError, validation_handler)
    app.add_exception_handler(CustomException, custom_base_handler)
    app.add_exception_handler(UserNotFoundException, custom_base_handler)
    app.add_exception_handler(UserPasswordNotMatchException, custom_base_handler)
    app.add_exception_handler(UserAlreadyExistsException, custom_base_handler)
    app.add_exception_handler(CrawlFailedException, custom_base_handler)
    app.add_exception_handler(FirecrawlConnectionException, custom_base_handler)
    app.add_exception_handler(FirecrawlContainerException, custom_base_handler)
    app.add_exception_handler(InvalidRequestException, custom_base_handler)
    app.add_exception_handler(NotebookNotFoundException, custom_base_handler)
    app.add_exception_handler(ChatNotFoundException, custom_base_handler)
    app.add_exception_handler(InvalidTokenException, custom_base_handler)
    app.add_exception_handler(ExpiredRefreshTokenException, custom_base_handler)
    app.add_exception_handler(InvalidRefreshTokenException, custom_base_handler)
    app.add_exception_handler(InvalidGoogleTokenException, custom_base_handler)
    app.add_exception_handler(GoogleClientIdMismatchException, custom_base_handler)
    app.add_exception_handler(OAuthAccountConflictException, custom_base_handler)
    app.add_exception_handler(InvalidUserException, custom_base_handler)
