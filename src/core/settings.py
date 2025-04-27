from datetime import timedelta
import enum
import pathlib

from pydantic_settings import BaseSettings
from pydantic import Field, MySQLDsn


class LogLevelsEnum(enum.StrEnum):
    FATAL = "FATAL"
    ERROR = "ERROR"
    WARN = "WARN"
    INFO = "INFO"
    DEBUG = "DEBUG"


class DataBaseConfig(BaseSettings):
    scheme: str = Field("mysql+pymysql", alias="DB_SCHEME")
    username: str = Field(alias="DB_USERNAME")
    password: str = Field(alias="DB_PASSWORD")
    host: str = Field(alias="DB_HOSTNAME")
    port: int = Field(alias="DB_PORT")
    path: str = Field(alias="DB_NAME")


class Settings(BaseSettings):
    DATABASE_URL: MySQLDsn = MySQLDsn.build(**DataBaseConfig().model_dump())
    VERSION_PREFIX: str
    LOG_LEVEL: LogLevelsEnum
    CHECKSUM_SALT: str
    SIGNATURE_KEY_PATH: pathlib.Path
    JWT_VALID_PERIOD: timedelta


_settings = None


def get() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
