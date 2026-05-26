from fastapi import Request
from fastapi.responses import JSONResponse
import uuid


class AppException(Exception):
    def __init__(self, status_code: int, code: str, message: str):
        self.status_code = status_code
        self.code = code
        self.message = message


class NotFoundError(AppException):
    def __init__(self, resource: str):
        super().__init__(404, "NOT_FOUND", f"{resource} no encontrado")


class UnauthorizedError(AppException):
    def __init__(self, message: str = "No autenticado"):
        super().__init__(401, "UNAUTHORIZED", message)


class ForbiddenError(AppException):
    def __init__(self, message: str = "Sin permisos suficientes"):
        super().__init__(403, "FORBIDDEN", message)


class ConflictError(AppException):
    def __init__(self, message: str):
        super().__init__(409, "CONFLICT", message)


async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.code,
            "message": exc.message,
            "trace_id": str(uuid.uuid4()),
            "path": str(request.url),
        },
    )


async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "error": "INTERNAL_SERVER_ERROR",
            "message": "Error interno del servidor",
            "trace_id": str(uuid.uuid4()),
            "path": str(request.url),
        },
    )
