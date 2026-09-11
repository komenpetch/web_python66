from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from pwdlib import PasswordHash

router = APIRouter()

SECRET_KEY = "secret_key"
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

password_hash = PasswordHash.recommended()
hashed_password = password_hash.hash("1234")

users = {
    "admin": 
    {
        "username": "admin",
        "password": hashed_password
    }
}

blacklist = set()

@router.post("/login")
async def login( from_data: OAuth2PasswordRequestForm = Depends()):
    print(from_data.password)
    user = users.get(from_data.username)
    
    print(user["password"])
    
    # if not user or not user["password"] == from_data.password:
    if not user or not password_hash.verify(from_data.password, user["password"]):
        return HTTPException(status_code=400, detail="Incorrect username or password")
    
    print(user)
    
    exprires = datetime.now(timezone.utc) + timedelta(minutes=10)
    
    token = jwt.encode({
        "sub": user["username"],
        "exp": exprires # Optional
        },
        SECRET_KEY, algorithm=ALGORITHM
        )

    return {
        "token": token,
        "type": "bearer"
        }
    
def get_current_user(token: str = Depends(oauth2_scheme)):
    
    if token in blacklist:
        raise HTTPException(status_code=401, detail="Token has been revoked")
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        print(f"Current user: {username}")
        
        return username
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
@router.get("/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    blacklist.add(token)
    
    return {
        "message": "Logged out successfully"
    }