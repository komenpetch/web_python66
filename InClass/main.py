from fastapi import FastAPI, Request

app = FastAPI()


@app.get("/")
async def root():
    return {"Hello": "World"}

@app.get("/items/{id1}/{id2}")
async def foo(id1: int, id2: str):
    return {"foo": str(id1) + " " + id2}

@app.get("/check_body")
async def check_body(request: Request):
    body = await request.json()
    print(body["id"], body["name"])
    return body