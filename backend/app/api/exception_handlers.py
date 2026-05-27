from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.domain.exceptions import (
    AppAuthenticationError,
    AppConflictError,
    AppNotFoundError,
    AppPermissionError,
    AppValidationError,
)


def _json_error_response(status_code: int, detail: str) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"detail": detail})


async def _conflict_handler(
    _: Request,
    exc: AppConflictError,
) -> JSONResponse:
    return _json_error_response(status.HTTP_409_CONFLICT, str(exc))


async def _not_found_handler(
    _: Request,
    exc: AppNotFoundError,
) -> JSONResponse:
    return _json_error_response(status.HTTP_404_NOT_FOUND, str(exc))


async def _permission_handler(
    _: Request,
    exc: AppPermissionError,
) -> JSONResponse:
    return _json_error_response(status.HTTP_403_FORBIDDEN, str(exc))


async def _authentication_handler(
    _: Request,
    exc: AppAuthenticationError,
) -> JSONResponse:
    return _json_error_response(status.HTTP_401_UNAUTHORIZED, str(exc))


async def _validation_handler(
    _: Request,
    exc: AppValidationError,
) -> JSONResponse:
    return _json_error_response(status.HTTP_422_UNPROCESSABLE_ENTITY, str(exc))


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppConflictError, _conflict_handler)
    app.add_exception_handler(AppNotFoundError, _not_found_handler)
    app.add_exception_handler(AppPermissionError, _permission_handler)
    app.add_exception_handler(AppAuthenticationError, _authentication_handler)
    app.add_exception_handler(AppValidationError, _validation_handler)
