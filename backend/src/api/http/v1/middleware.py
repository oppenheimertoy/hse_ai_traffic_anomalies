from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from src.domain import errors


def add_exception_handlers(app: FastAPI) -> None:
    """Register simple handlers that convert domain errors to HTTP responses."""

    @app.exception_handler(errors.DomainError)
    async def handle_domain_error(request: Request, exc: errors.DomainError) -> JSONResponse:  # noqa: ARG001
        status = getattr(exc, "status_code", 400)
        return JSONResponse(status_code=status, content={"detail": str(exc)})
