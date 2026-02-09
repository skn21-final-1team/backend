class CustomException(Exception):
    code: int = 500
    message: str = "서버 에러가 발생했습니다."

    def __init__(
        self,
        message: str | None = None,
        code: int | None = None,
    ):
        self.message = message or self.message
        self.code = code or self.code
