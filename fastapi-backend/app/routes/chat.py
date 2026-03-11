from fastapi import APIRouter, Depends
from typing import Annotated
from pydantic import BaseModel
from app.utils.auth import get_current_user
from app.utils.index import create_api_response

router = APIRouter()

class ChatMessage(BaseModel):
    message: str

@router.post("/chat")
async def chat(message: ChatMessage, current_user: Annotated[dict, Depends(get_current_user)]):
    print(f"Received message from user {current_user['uid']}: {message.message}")
    return create_api_response(msg="Message received", data={"user_id": current_user['uid'], "message": message.message})
    