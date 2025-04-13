from fastapi import FastAPI
from backend.routes.fragrance.fragrance import router as fragrance_router


app = FastAPI()


app.include_router(fragrance_router)