from pydantic_settings import BaseSettings



class Settings(BaseSettings):
    database_url: str
    sync_database_url: str
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"  
    jwt_access_token_expire_minutes: int = 30  
    cookie_name: str = "access_token"
    cookie_secure: bool = True
    cookie_httponly: bool = True
    cookie_samesite: str = "lax"


    class Config:
        env_file = ".env"


settings = Settings()