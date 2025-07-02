from logging.config import dictConfig

from storeapi.config import DevConfig, config


def configure_logging() -> None:
    dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "console": {
                "class": "logging.Formatter",
                "datefmt": "%Y-%m-%dT%H:%M:%S",
                "format": "%(name)s:%(lineno)d - %(message)s",
            },
            "file": {
                "class": "logging.Formatter",
                "datefmt": "%Y-%m-%dT%H:%M:%S",
                "format": "%(asctime)s.%(msecs)03dz | %(levelname)-8s | %(name)s:%(lineno)d - %(message)s",
            }
        },
        "handlers": {
            "default": {
                "class": "rich.logging.RichHandler",
                "level": "DEBUG",
                "formatter": "console",
            },
            "rotating_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "DEBUG",
                "formatter": "file",
                "filename": "storeapi.log",
                "maxBytes": 10 * 1024 * 1024,  # 10MB
                "backupCount": 5,
                "encoding": "utf8",
            }
        },
        "loggers": {
            "uvicorn": {
                "handlers": ["default", "rotating_file"],
                "level": "INFO",
            },
            "storeapi": {
                "handlers": ["default", "rotating_file"],
                "level": "DEBUG" if isinstance(config, DevConfig) else "INFO",
                "propagate": False  # storeapi.*에서 발생한 모든 로그는 root로그로 보내지 않겠다는 설정
            },
            "databases": {
                "handlers": ["default"],
                "level": "WARNING",
            },
            "aiosqlite": {
                "handlers": ["default"],
                "level": "WARNING",
            },
            "mysql": {
                "handlers": ["default"],
                "level": "WARNING",
            }
        },

    })
