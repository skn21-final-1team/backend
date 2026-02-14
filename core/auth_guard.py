from collections.abc import Callable

from fastapi import Request
from fastapi.routing import APIRoute
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response
from starlette.routing import Match

from core.config import get_settings
from core.exceptions.user import user_unauthorized_exception
from core.security import decode_token
from db.database import get_db_context
from models.users import UserModel

settings = get_settings()


def public(func: Callable) -> Callable:
    func._is_public = True
    return func


class AuthMiddleware(BaseHTTPMiddleware):
    EXEMPT_PATHS = {"/docs", "/redoc", "/openapi.json", f"{settings.api_str}/openapi.json", "/"}

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request.state.user = None

        if self._is_exempt_path(request.url.path):
            return await call_next(request)

        if self._should_skip_auth(request):
            return await call_next(request)

        token = self._extract_token(request)
        if token is None:
            return user_unauthorized_exception()

        user = self._authenticate(token)
        if user is None:
            return user_unauthorized_exception()

        request.state.user = user
        return await call_next(request)

    def _is_exempt_path(self, path: str) -> bool:
        return path in self.EXEMPT_PATHS

    def _should_skip_auth(self, request: Request) -> bool:
        for route in request.app.routes:
            if isinstance(route, APIRoute):
                match, _ = route.matches(request.scope)
                if match == Match.FULL:
                    return getattr(route.endpoint, "_is_public", False)
        return True

    def _extract_token(self, request: Request) -> str | None:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None
        return auth_header.removeprefix("Bearer ")

    def _authenticate(self, token: str) -> UserModel | None:
        try:
            payload = decode_token(token)
        except Exception:
            return None

        if payload.get("type") != "access":
            return None

        user_id = payload.get("sub")
        if user_id is None:
            return None

        with get_db_context() as db:
            return db.query(UserModel).filter(UserModel.id == int(user_id)).first()
