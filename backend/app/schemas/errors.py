from pydantic import BaseModel


class ErrorResponse(BaseModel):
    error: str
    request_id: str | None = None


class ValidationErrorResponse(BaseModel):
    error: str
    details: list
    request_id: str | None = None
