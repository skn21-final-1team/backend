from core.exceptions.base import CustomException

class ChatNotFoundException(CustomException):
    """채팅을 찾을 수 없을 때 발생"""

    def __init__(self):
        super().__init__("존재하지 않는 채팅입니다.", code=404)