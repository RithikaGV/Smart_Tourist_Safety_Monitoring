"""
middleware/error_handler.py
Central exception handlers - registered once in app.py via register_error_handlers(app).
"""
from fastapi import Request
from fastapi.responses import JSONResponse
from pymongo.errors import DuplicateKeyError


def register_error_handlers(app):
    @app.exception_handler(DuplicateKeyError)
    async def duplicate_key_handler(request: Request, exc: DuplicateKeyError):
        return JSONResponse(status_code=409, content={"success": False, "message": "Duplicate value", "details": str(exc)})

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        print(f"[error] {request.method} {request.url.path} -> {exc}")
        return JSONResponse(status_code=500, content={"success": False, "message": str(exc) or "Internal server error"})
