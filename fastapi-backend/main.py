from fastapi import FastAPI
import uvicorn


app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


def start():
    """Launched with `uv run dev` at root level"""
    uvicorn.run("main:app", host="127.0.0.1", port=8081, reload=True)

if __name__ == "__main__":
    start()
