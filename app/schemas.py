from pydantic import BaseModel

class Phone(BaseModel):
    phone_no: str

class PhoneCreate(Phone):
    pass

class PhoneResponse(Phone):
    id: int
    class Config:
        from_attributes = True

class Student(BaseModel):
    id: int | None = None
    name: str
    score: float

# in
class StudentCreate(Student):
    # pass
    phones: list[PhoneCreate]

# out
class StudentResponse(Student):
    id: int
    phones: list[PhoneResponse]

    class Config:
        from_attributes = True
