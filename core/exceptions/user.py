from core.exceptions.base import CustomException


class UserNotFoundException(CustomException):
    """유저를 찾을 수 없을 때 발생"""

    def __init__(self):
        super().__init__("존재하지 않는 사용자입니다.", code=404)


class UserPasswordNotMatchException(CustomException):
    """유저 비밀번호가 일치하지 않을 때 발생"""

    def __init__(self):
        super().__init__("비밀번호가 일치하지 않습니다.", code=401)
