import logging

from core import settings


def init_logging(log_level: settings.LogLevelsEnum = None) -> None:
    env_settings = settings.get()

    log_level = log_level or env_settings.LOG_LEVEL
    logger = logging.getLogger()
    logger.setLevel(log_level)
    logger.info("Global log level set to %s", log_level)
