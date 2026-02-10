from core.exceptions.base import CustomException


class CrawlFailedException(CustomException):
    code = 502
    message = "크롤링에 실패했습니다."


class FirecrawlConnectionException(CustomException):
    code = 503
    message = "Firecrawl 서버에 연결할 수 없습니다."


class FirecrawlContainerException(CustomException):
    code = 503
    message = "Firecrawl 컨테이너를 시작할 수 없습니다."
