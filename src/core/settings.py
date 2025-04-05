from pydantic_settings import BaseSettings
from pydantic import Field, MySQLDsn


class DataBaseConfig(BaseSettings):
    scheme: str = Field("mysql+pymysql", alias="DB_SCHEME")
    username: str = Field(alias="DB_USERNAME")
    password: str = Field(alias="DB_PASSWORD")
    host: str = Field(alias="DB_HOST")
    port: int = Field(alias="DB_PORT")
    path: str = Field(alias="DB_NAME")

class Settings(BaseSettings):
    DATABASE_URL: MySQLDsn = MySQLDsn.build(**BaseSettings().model_dump())
    VERSION_PREFIX: str


_settings = None

def get() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
