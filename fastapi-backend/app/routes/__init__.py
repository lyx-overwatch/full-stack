from fastapi import FastAPI, APIRouter
from .login import router as login_router
from .chat import router as chat_router

def common_include_router(app: FastAPI, api_router: APIRouter):
    """公共路由注册函数"""
    app.include_router(api_router,
    prefix="/api")

def register_routers(app: FastAPI):
    """注册所有路由"""
    common_include_router(app, login_router)
    common_include_router(app, chat_router)
    return app