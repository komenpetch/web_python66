from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt

router = APIRouter()

SECRET_KEY = "secret_key"
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

users = {
    "admin": 
    {
        "username": "admin",
        "password": "1234"
    }
}

@router.post("/login")
async def login( from_data: OAuth2PasswordRequestForm = Depends()):
    print(from_data.password)
    user = users.get(from_data.username)
    
    print(user["password"])
    
    if not user or not user["password"] == from_data.password:
        return HTTPException(status_code=400, detail="Incorrect username or password")
    
    token = jwt.encode({
        "sub": user["username"]
        },
        SECRET_KEY, algorithm=ALGORITHM
        )


    return {
        "token": token,
        "type": "bearer"
        }
    
def get_current_user(token: str = Depends(oauth2_scheme)):
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        print(f"Current user: {username}")
        
        return username
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")