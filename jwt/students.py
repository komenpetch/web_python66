from fastapi import APIRouter, Depends

from auth import get_current_user


router = APIRouter()

@router.get("/")
async def hello():
    return {"message": "Hello, World!"}


# Must require a valid token to access this endpoint
@router.get("/students")
async def get_students( username: str = Depends(get_current_user)):
    return {
        "message": "Login Successful",
        "user": username,
        "students": [
            {"id": 1, "name": "John"},
            {"id": 2, "name": "Jane"},
            {"id": 3, "name": "Jones"}
        ]
    }