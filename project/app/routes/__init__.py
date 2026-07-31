from fastapi import APIRouter

from app.core.config import settings
from app.routes.chat import router as chat_router
from app.routes.extract import router as extract_router
from app.routes.index import router as index_router


api_router = APIRouter(prefix=settings.API_PREFIX)
api_router.include_router(extract_router)
api_router.include_router(index_router)
api_router.include_router(chat_router)

__all__ = ["api_router"]

