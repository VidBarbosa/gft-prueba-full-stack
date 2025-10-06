from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi import status

class DomainError(Exception):
    def __init__(self, message: str, code: int = status.HTTP_400_BAD_REQUEST):
        self.message = message
        self.code = code

async def domain_error_handler(request: Request, exc: DomainError):
    return JSONResponse(status_code=exc.code, content={"detail": exc.message})
