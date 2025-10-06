import logging, sys
import structlog
from app.config import settings

def configure_logging():
    shared = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.TimeStamper(fmt="iso", key="ts"),
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]
    renderer = structlog.processors.JSONRenderer() if settings.log_format.lower() == "json" else structlog.dev.ConsoleRenderer()
    structlog.configure(
        processors=shared + [renderer],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    logging.basicConfig(format="%(message)s", stream=sys.stdout, level=getattr(logging, settings.log_level.upper(), logging.INFO))

log = structlog.get_logger()
