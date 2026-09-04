
from typing import List

from fastapi import Depends, FastAPI, HTTPException 
from sqlalchemy import  create_engine
from sqlalchemy.orm import Session 
from sqlalchemy.ext.declarative import declarative_base

from .models import PhoneDB, StudentDB, SubjectDB
from .schemas import PhoneCreate, PhoneResponse, StudentCreate, StudentResponse, SubjectCreate, SubjectResponse

from .database import Base, get_db, engine

#Base.metadata.drop_all(bind=engine)
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

# student

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
    
    db_student.name = std.name
    db_student.score = std.score
    
    for phone in std.phones:
        if not any(p.phone_no == phone.phone_no for p in db_student.phones):
            db_student.phones.append(PhoneDB(phone_no=phone.phone_no))
    
    # for key, value in std.model_dump().items():
    #     setattr(db_student, key, value)
    db.commit()
    db.refresh(db_student)
    return db_student

# Phone

@app.get("/phones", response_model=List[PhoneResponse])
async def read_phones( db: Session = Depends(get_db) ):
    return db.query(PhoneDB).all()

@app.get("/phones/{phone_id}", response_model=PhoneResponse)
async def read_phone(phone_id: int, db: Session = Depends(get_db)):
    db_phone = db.query(PhoneDB).filter(PhoneDB.id == phone_id).first()
    if db_phone is None:
        raise HTTPException(status_code = 404, detail = "Phone not found")
    return db_phone

@app.put("/phones/{phone_id}", response_model=PhoneResponse)
async def update_phone(phone_id: int, phone: PhoneCreate, db: Session = Depends(get_db)):
    db_phone = db.query(PhoneDB).filter(PhoneDB.id == phone_id).first()
    if db_phone is None:
        raise HTTPException(status_code = 404, detail = "Phone not found")
    
    db_phone.phone_no = phone.phone_no
    db.commit()
    db.refresh(db_phone)
    return db_phone

@app.delete("/phones/{phone_id}")
async def delete_phone(phone_id: int, db: Session = Depends(get_db)):
    db_phone = db.query(PhoneDB).filter(PhoneDB.id == phone_id).first()
    if db_phone is None:
        raise HTTPException(status_code = 404, detail = "Phone not found")
    db.delete(db_phone)
    db.commit()
    return { "message": "Phone deleted"}


# subject
@app.post("/subjects", response_model=SubjectResponse)
async def create_subject(subject: SubjectCreate, db: Session = Depends(get_db)):
    db_subject = SubjectDB(name=subject.name)
    db.add(db_subject)
    db.commit()
    db.refresh(db_subject)
    return db_subject

@app.get("/subjects", response_model=List[SubjectResponse])
async def read_subjects(db: Session = Depends(get_db)):
    return db.query(SubjectDB).all()

@app.post("/students/{student_id}/subjects/{subject_id}")
async def register_subject(student_id: int, subject_id: int, db: Session = Depends(get_db)):
    student = db.query(StudentDB).filter(StudentDB.id == student_id).first()
    subject = db.query(SubjectDB).filter(SubjectDB.id == subject_id).first()

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")

    student.subjects.append(subject)
    db.commit()
    return {"message": "Subject registered for student"}
