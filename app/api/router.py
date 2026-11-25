from fastapi import APIRouter
from .endpoints.web import router as web_pages_router
from .endpoints.documents import router as documents_router
from .endpoints.chat import router as chat_router

router = APIRouter()

# Include specific routers
router.include_router(web_pages_router)
router.include_router(documents_router)
router.include_router(chat_router)