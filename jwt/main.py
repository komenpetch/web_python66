from fastapi import FastAPI
from students import router as student_router
from auth import router as auth_router

app = FastAPI()

app.include_router(student_router)
app.include_router(auth_router)