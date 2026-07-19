from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    db_host: str
    db_port: str
    db_user: str
    db_password: str
    db_name: str

    model_config = SettingsConfigDict(env_file=".env")

    
settings = Settings()
print(settings.db_user)
print(settings.db_password)
print(settings.db_host)
print(settings.db_port)
print(settings.db_name)
