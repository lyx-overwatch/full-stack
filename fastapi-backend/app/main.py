from fastapi import FastAPI
from app.routes import register_routers
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.utils.index import create_api_response

app = FastAPI()

# 注册所有路由
app = register_routers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有头部)
)

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    return create_api_response(data=None, msg=str(exc.detail), code=exc.status_code)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return create_api_response(data=exc.errors(), msg="Validation Error", code=422)


@app.get("/")
async def root():
    return {"message": "Hello World"}
