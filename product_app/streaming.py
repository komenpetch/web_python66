import asyncio

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from .chatbot import bot_reply
from .database import SessionLocal

router = APIRouter()


# stream the bot's answer word by word, like a typing effect
@router.get("/chat/stream")
async def chat_stream(message: str):
    async def generate():
        db = SessionLocal()
        try:
            reply = bot_reply(db, message)
        finally:
            db.close()

        for line in reply.splitlines(keepends=True):
            for word in line.split(" "):
                await asyncio.sleep(0.05)
                yield word if word.endswith("\n") else word + " "

    return StreamingResponse(generate(), media_type="text/plain")
