from typing import List
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import Column, Float, Integer, String, create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

#Step 1 SQL LITE

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
# Data model        
class StudentDB(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    score = Column(Float, index=False)
    
class Student(BaseModel):
    id: int
    name: str
    score: float

# IN
class StudentCreate(Student):
    pass

# OUT
class StudentResponse(Student):
    id: int
    class Config:
        from_attributes = True
        
Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.post("/students", response_model=StudentResponse)
async def create_students(student: StudentCreate, db: Session = Depends(get_db)):
    db_student = StudentDB(**student.model_dump())
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

@app.get("/students", response_model=List[StudentResponse])
async def get_students(db: Session = Depends(get_db)):
    students = db.query(StudentDB).all()
    return students

@app.get("/students/{student_id}", response_model=StudentResponse)
async def get_student(student_id: int, db: Session = Depends(get_db)):
    db_student = db.query(StudentDB).filter(StudentDB.id == student_id).first()
    if db_student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return db_student

@app.delete("/students/{student_id}")
async def delete_student(student_id: int, db: Session = Depends(get_db)):
    db_student = db.query(StudentDB).filter(StudentDB.id == student_id).first()
    if db_student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    db.delete(db_student)
    db.commit()
    return {"message": "Student deleted"}

@app.put("/students/{student_id}", response_model=StudentResponse)
async def update_student(student_id: int, std: StudentCreate, db: Session = Depends(get_db)):
    db_student = db.query(StudentDB).filter(StudentDB.id == student_id).first()
    if db_student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    for key, value in std.model_dump().items():
        setattr(db_student, key, value)
    db.commit()
    db.refresh(db_student)
    return db_student