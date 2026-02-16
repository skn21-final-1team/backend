from core.exceptions.base import CustomException


class DirectoryNotFoundException(CustomException):
    """디렉토리를 찾을 수 없을 때 발생"""

    def __init__(self):
        super().__init__("존재하지 않는 디렉토리입니다.", code=404)
