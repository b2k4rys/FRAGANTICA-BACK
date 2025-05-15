from fastapi import FastAPI
from backend.routes.fragrance.fragrance import router as fragrance_router
from backend.routes.auth.auth import router as auth_router


app = FastAPI()


app.include_router(fragrance_router)
app.include_router(auth_router)