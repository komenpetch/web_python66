import asyncio
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

app = FastAPI()

@app.get("/")
def hello():
    return("message:" "Hello warodom")

@app.get("/normal")
async def normal():
    lines = []
    for i in range(1,6):
        await asyncio.sleep(1)
        lines.append(f"chuck {i}")
    return{"data": lines}

@app.get("/stream")
async def stream():
    async def generate():
        for i in range(1,6):
            await asyncio.sleep(1)
            yield f"check {i}\n "
    return StreamingResponse(generate(), media_type="text/plain")

SENTENCE = "Streaming the server is working"

@app.get("/chat")
async def chat():
    async def generate():
        for word in SENTENCE.split():
            await asyncio.sleep(0.3)
            yield word + " "
    return StreamingResponse(generate(), media_type="text/plain")

@app.get("/progress")
async def progress():
    async def generate():
        for percent in range(0, 101, 10):
            await asyncio.sleep(0.5)
            yield f"{percent} done \n"
        yield "Done!!!\n"
    return StreamingResponse(generate(), media_type="text/plain")