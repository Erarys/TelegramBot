from pydantic import BaseSettings, SecretStr

class Settings(BaseSettings):
    bot_token: SecretStr

    class Config:
        env_file = ".env"
        env_file_encoding = "UTF-8"


config = Settings()