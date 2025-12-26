from typing import Callable, Iterable

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from jwt.exceptions import DecodeError, ExpiredSignatureError
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from src.domain import errors
from src.domain.auth.entity import Credentials
from src.domain.auth.service import AuthService, JWTAuthenticationStrategy
from src.domain.auth.errors import TokenExpiredError, TokenNotFoundError

def add_exception_handlers(app: FastAPI) -> None:
    """Register simple handlers that convert domain errors to HTTP responses."""

    @app.exception_handler(errors.DomainError)
    async def handle_domain_error(
        request: Request, exc: errors.DomainError,
    ) -> JSONResponse:  # noqa: ARG001
        status = getattr(exc, "status_code", 400)
        return JSONResponse(status_code=status, content={"detail": str(exc)})


class JwtAuthMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: FastAPI,
        authentication_service: AuthService,
        excluded_paths: Iterable[str] | None = None,
    ) -> None:
        super().__init__(app)

        self._authentication_service = authentication_service
        self._excluded_paths = tuple(excluded_paths or ())

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint,
    ) -> Response:
        
        if request.url.path.startswith(self._excluded_paths):
            return await call_next(request)
        
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return self._unauthorized("Missing bearer token.", "unknown")
        parts = auth_header.split(" ", 1)
        if len(parts) != 2:
            return self._unauthorized("Incorrect authentication credentials.", "unknown")
        auth_method, access_token = parts
        if not auth_method or not access_token:
            return self._unauthorized("Incorrect authentication credentials.", "unknown")
        try:
            credentials: Credentials = await self._authentication_service.authenticate(
                auth_method,
                access_token,
            )
            request.state.user_id = credentials.user_id
            request.state.username = credentials.username
        except TokenExpiredError:
            if auth_method.strip().lower() != "bearer":
                return self._unauthorized("Token is expired", "BASIC")
            refresh_token = request.headers.get(
                "Refresh-Token",
            ) or request.cookies.get("refresh_token")
            if not refresh_token:
                return self._unauthorized("Access token expired.", "JWt")
            try:
                creds: Credentials = await self._authentication_service.authenticate(
                    method="Bearer",
                    content=refresh_token,
                )
            except (DecodeError, TokenNotFoundError) as exc:
                return self._unauthorized(f"Invalid refresh token. {exc}", 'JWT')
            request.state.new_access_token = self._authentication_service.create_access_token(
                username=creds.username,
                user_id=creds.user_id,
            )
            request.state.new_refresh_token = self._authentication_service.create_refresh_token(
                username=creds.username,
                user_id=creds.user_id,
            )
        except DecodeError as e:
            return self._unauthorized(f"Invalid token. {e}", method='JWT')

        response = await call_next(request)
        new_access_token = getattr(request.state, "new_access_token", None)
        new_refresh_token = getattr(request.state, "new_refresh_token", None)
        if new_access_token:
            response.headers["X-Access-Token"] = new_access_token
        return response

    def _unauthorized(self, detail: str, method: str) -> JSONResponse:
        headers = {"WWW-Authenticate": method}
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": detail},
            headers=headers,
        )
