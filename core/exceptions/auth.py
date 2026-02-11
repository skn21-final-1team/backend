from core.exceptions.base import CustomException


class InvalidTokenException(CustomException):
    def __init__(self):
        super().__init__("유효하지 않은 토큰입니다.", code=401)


class ExpiredRefreshTokenException(CustomException):
    def __init__(self):
        super().__init__("유효하지 않거나 만료된 Refresh Token입니다.", code=401)


class InvalidRefreshTokenException(CustomException):
    def __init__(self):
        super().__init__("Refresh Token이 아닙니다.", code=401)


class InvalidGoogleTokenException(CustomException):
    def __init__(self):
        super().__init__("유효하지 않은 Google 토큰입니다.", code=401)


class GoogleClientIdMismatchException(CustomException):
    def __init__(self):
        super().__init__("Google Client ID가 일치하지 않습니다.", code=401)


class OAuthAccountConflictException(CustomException):
    def __init__(self):
        super().__init__("해당 이메일은 일반 로그인으로 등록된 계정입니다.", code=409)
