import logging
import sys
import structlog
from app.core.config import settings


def setup_logging() -> None:
    """
    Configure structured logging for the application.
    """

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.INFO,
    )

    structlog.configure(
        processors=[
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    log = structlog.get_logger()

    log.info(
        "logging_initialized",
        app=settings.app_name,
        environment=settings.environment,
    )