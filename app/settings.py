from datetime import timedelta
from secrets import token_hex

from pydantic import AnyUrl, BaseSettings


class Settings(BaseSettings):
    port: int = 5001
    mongo_url: AnyUrl = AnyUrl(
        "mongodb://127.0.0.1:27017",
        scheme="mongodb",
        host="127.0.0.1",
    )
    mongo_db_name: str = "neoplasm-users"
    mongo_collection_name: str = "users"
    token_iss: str = "nplsm"
    token_algorithm: str = "HS256"
    access_token_secret: str = str(token_hex(512))
    access_token_expiration: int = 5
    refresh_token_secret: str = str(token_hex(512))
    refresh_token_expiration: int = 7 * 24 * 60

    @property
    def access_token_expiration_timedelta(self) -> timedelta:
        return timedelta(minutes=self.access_token_expiration)

    @property
    def refresh_token_expiration_timedelta(self) -> timedelta:
        return timedelta(minutes=self.refresh_token_expiration)


settings = Settings()
