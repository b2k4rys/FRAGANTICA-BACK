from pydantic_settings import BaseSettings
import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url


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
    cloud_name: str
    api_key: str
    api_secret: str
    secure: bool = True



    class Config:
        env_file = ".env"
settings = Settings()

cloudinary.config( 
    cloud_name = settings.cloud_name, 
    api_key = settings.api_key, 
    api_secret = settings.api_secret, 
    secure=settings.secure
)

