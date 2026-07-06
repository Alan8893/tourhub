import uuid
import time
import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


log = structlog.get_logger()


class RequestContextMiddleware(BaseHTTPMiddleware):
    """
    Adds request_id + basic request logging
    """

    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        start_time = time.time()

        # attach request_id to request state
        request.state.request_id = request_id

        response: Response = await call_next(request)

        process_time = time.time() - start_time

        log.info(
            "http_request",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            request_id=request_id,
            process_time_ms=round(process_time * 1000, 2),
        )

        response.headers["X-Request-ID"] = request_id

        return response