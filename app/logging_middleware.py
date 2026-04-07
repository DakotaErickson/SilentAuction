import json
import logging
import time
import uuid

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",  # Raw message only — we're emitting JSON
)
logger = logging.getLogger("auction")


class LoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = str(uuid.uuid4())[:8]
        start = time.perf_counter()

        # Capture request body for POST/PUT so you can see bad bid payloads
        body = None
        if request.method in ("POST", "PUT", "PATCH"):
            try:
                raw = await request.body()
                body = json.loads(raw) if raw else None
                # Re-inject body so FastAPI can still read it
                async def receive():
                    return {"type": "http.request", "body": raw}
                request._receive = receive
            except Exception:
                body = "<unreadable>"

        response = await call_next(request)

        duration_ms = round((time.perf_counter() - start) * 1000, 1)
        status_code = response.status_code

        log = {
            "req_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "query": str(request.url.query) or None,
            "status": status_code,
            "duration_ms": duration_ms,
            "client": request.client.host if request.client else None,
        }

        if body:
            # Redact contact info from bid payloads before logging
            if isinstance(body, dict):
                log["body"] = {k: ("***" if k == "contact" else v) for k, v in body.items()}

        # Log errors at WARNING/ERROR level so they stand out
        if status_code >= 500:
            logger.error(json.dumps(log))
        elif status_code >= 400:
            logger.warning(json.dumps(log))
        else:
            logger.info(json.dumps(log))

        return response