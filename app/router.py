from fastapi import APIRouter
from app.users.router import router as user_router
from app.auth.router import router as auth_router

router = APIRouter()

router.include_router(user_router)
router.include_router(auth_router)
