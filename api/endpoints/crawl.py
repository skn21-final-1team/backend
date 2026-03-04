from fastapi import APIRouter

from core.auth_guard import public
from schemas.crawl import CrawlRequestBody
from schemas.response import BaseResponse
from services.crawl import crawl_service

router = APIRouter()


@router.post(
    "",
    response_model=BaseResponse[bool],
)
@public
async def crawl(body: CrawlRequestBody) -> BaseResponse[bool]:
    result = await crawl_service.crawl_and_save(body)
    return BaseResponse.ok(data=result)
