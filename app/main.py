
from typing import List

from fastapi import Depends, FastAPI, HTTPException 
from sqlalchemy import  create_engine
from sqlalchemy.orm import Session 
from sqlalchemy.ext.declarative import declarative_base

from .models import PhoneDB, StudentDB
from .schemas import StudentCreate, StudentResponse

from .database import Base, get_db, engine

Base.metadata.create_all(bind=engine)
app = FastAPI()
@app.post("/students", response_model=StudentResponse)
async def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    # db_student = StudentDB(**student.model_dump())
    db_student = StudentDB(
        name=student.name,
        score= student.score,
        phones = [PhoneDB(phone_no=phone.phone_no) for phone in student.phones],
    )
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

@app.get("/students", response_model=List[StudentResponse])
async def read_students( db: Session = Depends(get_db) ):
    return db.query(StudentDB).all()

@app.get("/students/{student_id}", response_model=StudentResponse)
async def read_student(student_id: int, db: Session = Depends(get_db)):
    db_student = db.query(StudentDB).filter(StudentDB.id == student_id).first()
    if db_student is None:
        raise HTTPException(status_code = 404, detail = "Student not found")
    return db_student

@app.delete("/students/{student_id}")
async def delete_student(student_id: int, db: Session = Depends(get_db)):
    db_student = db.query(StudentDB).filter(StudentDB.id == student_id).first()
    if db_student is None:
        raise HTTPException(status_code = 404, detail = "Student not found")
    db.delete(db_student)
    db.commit()
    return { "message": "Student deleted"}

@app.put("/students/{student_id}", response_model=StudentResponse)
async def update_student(student_id: int, std: StudentCreate, db: Session = Depends(get_db)):
    db_student = db.query(StudentDB).filter(StudentDB.id == student_id).first()
    if db_student is None:
        raise HTTPException(status_code = 404, detail = "Student not found")
    for key, value in std.model_dump().items():
        setattr(db_student, key, value)
    db.commit()
    db.refresh(db_student)
    return db_student