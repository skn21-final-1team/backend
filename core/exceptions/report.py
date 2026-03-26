from core.exceptions.base import CustomException


class ReportWorkflowAlreadyRunningException(CustomException):
    def __init__(self):
        super().__init__("해당 노트북의 리포트 워크플로우가 이미 실행 중입니다.", code=409)
