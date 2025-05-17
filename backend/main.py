from fastapi import FastAPI
from backend.routes.fragrance.fragrance import router as fragrance_router
from backend.routes.auth.auth import router as auth_router
from backend.core.configs.config import settings
from fastapi_csrf_protect import CsrfProtect
from pydantic_settings import BaseSettings

app = FastAPI()

class CsrfSettings(BaseSettings):
    secret_key: str = settings.jwt_secret_key 
    cookie_samesite: str = settings.cookie_samesite
    cookie_secure: bool = settings.cookie_secure

@CsrfProtect.load_config
def get_csrf_config():
    return CsrfSettings()

app.include_router(fragrance_router)
app.include_router(auth_router)