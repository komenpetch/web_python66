import json
import asyncio
from fastapi import FastAPI, Request, HTTPException, Depends
import redis.asyncio as redis

app = FastAPI()

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

@app.get("/ping")
async def ping():
    return {"message": await r.ping()}

LIMITS = 5
WINDOW = 60  # seconds

async def rate_limiter(request: Request):
    ip = request.client.host
    key = f"rate:{ip}"
    
    count = await r.incr(key)
    if count == 1:
        await r.expire(key, WINDOW)
        
    if count > LIMITS:
        ttl = await r.ttl(key)
        raise HTTPException(
            status_code=429,
            detail=f"ยิงเกิน {LIMITS} ครั้งแล้ว รออีก {ttl} วินาที",
            headers={"Retry-After": str(ttl)}
        )
        
    return count

@app.get("/hello")
async def hello(count: int = Depends(rate_limiter)):
    return {"message": "สวัสดี, ", "used": count, "remaining": LIMITS - count}

def limiter(limit: int, window: int):
    async def _check(request: Request):
        key = f"rate:{request.client.path}:{request.client.host}"
        count = await r.incr(key)
        if count == 1:
            await r.expire(key, window)
        if count > limit:
            raise HTTPException(
                status_code=429,
                detail=f"Too many requests. Limit is {limit} per {window} seconds.")
    return _check

@app.post("/login", dependencies=[Depends(limiter(3, 60))])
async def login():
    return {"message": "พยายามล็อกอินสำเร็จ!"}

@app.get("/products", dependencies=[Depends(limiter(20, 60))])
async def products():
    return {"items": ["สินค้า 1", "สินค้า 2", "สินค้า 3"]}

@app.get("/slow-data")
async def slow_data():
    cached = await r.get("cache.slow_data")
    if cached:
        return {"source": "cache", "data": json.loads(cached)}
    
    await asyncio.sleep(3)  # Simulate slow processing
    data = {"data": "ข้อมูลที่ช้า"}
    
    await r.set("cache.slow_data", json.dumps(data), ex=30)  # Cache for 30 seconds
    return {"source": "generated", "data": data}