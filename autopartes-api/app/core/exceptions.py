from fastapi import Request
from fastapi.responses import JSONResponse


async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(status_code=422, content={"detail": str(exc)})


async def permission_error_handler(request: Request, exc: PermissionError):
    return JSONResponse(status_code=403, content={"detail": str(exc)})