from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

limiter = Limiter(
    key_func=get_remote_address,
    storage_url="redis://localhost:6379",
    )

app = FastAPI(title="Rate Limit Demo")
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

async def custom_rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={
            "success": False, 
            "message": "Rate limit exceeded. Please try again later.",
            "limit": str(exc.detail)},
    )
    
app.add_exception_handler(RateLimitExceeded, custom_rate_limit_exceeded_handler)

@app.get("/")
async def home():
    return {"message": "Welcome to the Rate Limit Demo!"}

@app.get("/limited")
@limiter.limit("5/minute")
async def limited_endpoint(request: Request):
    return {"message": "คุณเรียกใช้ endpoint นี้ได้สำเร็จ!"}

@app.post("/login")
@limiter.limit("3/minute")
async def login(request: Request):
    return {"message": "พยายามล็อกอินสำเร็จ!"}

@app.get("/products")
@limiter.limit("100/minute")
async def get_products(request: Request):
    return {"message": "รายการสินค้า!"}

# def get_user_id (request: Request):
#     if hasattr(request.state, "user_id"):
#         return request.state.user_id
#     return get_remote_address(request)

# limiter = Limiter(key_func=get_user_id)