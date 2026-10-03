from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    db_host: str
    db_port: str
    db_user: str
    db_password: str
    db_name: str

    
    jwt_secret_key :str
    jwt_algorithm: str
    jwt_access_token_expire_minutes: int
    
    
    model_config = SettingsConfigDict(env_file=".env")

    
settings = Settings()