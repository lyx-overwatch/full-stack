from fastapi import APIRouter,Depends
from typing import Annotated
from utils.index import create_api_response 

router = APIRouter()

@router.post("/login")
def login():
    return create_api_response(item={"message": "Login successful"})


async def common_parameters(q: str | None = None, skip: int = 0, limit: int = 100):
    return {"q": q, "skip": skip, "limit": limit}

CommonDeps = Annotated[dict, Depends(common_parameters)]

@router.get("/items/")
async def read_items(commons: CommonDeps):
    return commons


@router.get("/users/")
async def read_users(commons: CommonDeps):
    return commons
