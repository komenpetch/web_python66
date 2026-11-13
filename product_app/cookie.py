import secrets
from typing import Annotated

from fastapi import APIRouter, Cookie, HTTPException, Response
from pydantic import BaseModel, Field

router = APIRouter()

# session_id -> visitor name
sessions: dict[str, str] = {}


class NameIn(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)


@router.post("/set-name")
def set_name(body: NameIn, response: Response):
    session_id = secrets.token_urlsafe(32)
    sessions[session_id] = body.name
    response.set_cookie(key="session_id", value=session_id, max_age=3600, httponly=True)
    return {"message": f"remember {body.name}"}


@router.get("/welcome")
def welcome(session_id: Annotated[str | None, Cookie()] = None):
    name = sessions.get(session_id)
    if name is None:
        raise HTTPException(status_code=401, detail="don't know yet")
    return {"message": f"hi {name}", "name": name}


@router.get("/forget")
def forget(response: Response, session_id: Annotated[str | None, Cookie()] = None):
    sessions.pop(session_id, None)
    response.delete_cookie(key="session_id")
    return {"message": "i forget"}
