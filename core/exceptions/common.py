from core.exceptions.base import CustomException


class InvalidRequestException(CustomException):
    """정상적인 요청이 아닐 때"""

    def __init__(self):
        super().__init__("정상적인 요청이 아닙니다.", code=403)
