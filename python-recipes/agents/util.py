import logging
import logging.config
import os

from dotenv import load_dotenv

load_dotenv()

LOG_LEVEL = os.getenv("DND_AGENT_LOG_LEVEL", logging.WARN)

logging.config.dictConfig(
    {
        "version": 1,
        "disable_existing_loggers": True,
        "formatters": {
            "standard": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            }
        },
        "handlers": {
            "console": {
                "level": LOG_LEVEL,
                "class": "logging.StreamHandler",
                "formatter": "standard",
            }
        },
        "root": {"handlers": ["console"], "level": LOG_LEVEL},
        "loggers": {
            "langgraph": {
                "handlers": ["console"],
                "level": LOG_LEVEL,
                "propagate": True,
            },
            "langchain": {
                "handlers": ["console"],
                "level": LOG_LEVEL,
                "propagate": True,
            },
            "httpcore": {
                "handlers": ["console"],
                "level": "WARNING",
                "propagate": False,
            },
        },
    }
)


def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)
    return logger
