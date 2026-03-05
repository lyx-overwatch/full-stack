from fastapi import FastAPI
from routes import register_routers

app = FastAPI()

# 注册所有路由
app = register_routers(app)

@app.get("/")
async def root():
    return {"message": "Hello World"}
