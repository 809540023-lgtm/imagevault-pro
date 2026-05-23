from fastapi import APIRouter
from app.api.v1 import login, images, categories

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(images.router, prefix="/images", tags=["images"])
api_router.include_router(categories.router, prefix="/categories", tags=["categories"])
