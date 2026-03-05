from fastapi import FastAPI
from .login import router as login_router

def register_routers(app: FastAPI):
    """注册所有路由"""
    app.include_router(login_router)

    return app