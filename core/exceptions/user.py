from fastapi.responses import JSONResponse

from core.exceptions.base import CustomException


class UserNotFoundException(CustomException):
    """유저를 찾을 수 없을 때 발생"""

    def __init__(self):
        super().__init__("존재하지 않는 사용자입니다.", code=404)


class UserPasswordNotMatchException(CustomException):
    """유저 비밀번호가 일치하지 않을 때 발생"""

    def __init__(self):
        super().__init__("비밀번호가 일치하지 않습니다.", code=401)


class UserAlreadyExistsException(CustomException):
    """이미 존재하는 사용자일 때 발생"""

    def __init__(self):
        super().__init__("이미 존재하는 사용자입니다.", code=409)


class InvalidUserException(CustomException):
    """유저 정보가 유효하지 않을 때 발생"""

    def __init__(self):
        super().__init__("유저 정보가 유효하지 않습니다.", code=401)


def user_unauthorized_exception():
    """유저 인증이 필요할 때 사용, 미들웨어에서 사용하기위해 response로 반환"""
    return JSONResponse(
        status_code=401,
        content={"status": "error", "data": None, "message": "인증이 필요합니다."},
    )
