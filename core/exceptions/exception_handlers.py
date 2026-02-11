from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from core.exceptions.base import CustomException
from core.exceptions.chat import ChatNotFoundException
from core.exceptions.crawl import CrawlFailedException, FirecrawlConnectionException, FirecrawlContainerException
from core.exceptions.notebook import NotebookNotFoundException
from core.exceptions.user import UserAlreadyExistsException, UserNotFoundException, UserPasswordNotMatchException
from schemas.response import BaseResponse


def custom_base_handler(request: Request, exc: CustomException) -> JSONResponse:
    response = BaseResponse.error(message=exc.message, code=exc.code)
    return JSONResponse(status_code=exc.code, content=response.model_dump())


def init_exception_handlers(app: FastAPI):
    app.add_exception_handler(CustomException, custom_base_handler)
    app.add_exception_handler(UserNotFoundException, custom_base_handler)
    app.add_exception_handler(UserPasswordNotMatchException, custom_base_handler)
    app.add_exception_handler(UserAlreadyExistsException, custom_base_handler)
    app.add_exception_handler(CrawlFailedException, custom_base_handler)
    app.add_exception_handler(FirecrawlConnectionException, custom_base_handler)
    app.add_exception_handler(FirecrawlContainerException, custom_base_handler)
    app.add_exception_handler(NotebookNotFoundException, custom_base_handler)
    app.add_exception_handler(ChatNotFoundException, custom_base_handler)
