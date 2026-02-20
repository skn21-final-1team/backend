from core.exceptions.base import CustomException


class CrawlFailedException(CustomException):
    code = 502
    message = "크롤링에 실패했습니다."
