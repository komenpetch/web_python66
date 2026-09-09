from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Student(BaseModel):
    id: int
    name: str
    score: int


students: List[Student] = [
    Student(id=1, name="John Doe", score=20),
    Student(id=2, name="Jim Hanh", score=40),
    Student(id=3, name="Jack Gobert", score=55),
]


@app.get("/students", response_model=List[Student])
async def get_students():
    return students


@app.get("/students/{student_id}", response_model=Student)
async def get_student(student_id: int):
    for student in students:
        if student.id == student_id:
            return student

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Student not found",
    )


@app.post(
    "/students",
    response_model=Student,
    status_code=status.HTTP_201_CREATED,
)
async def create_student(student: Student):
    for existing_student in students:
        if existing_student.id == student.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Student with id {student.id} already exists",
            )

    students.append(student)
    return student


@app.delete("/students/{student_id}", status_code=status.HTTP_200_OK)
async def delete_student(student_id: int):
    for index, student in enumerate(students):
        if student.id == student_id:
            deleted_student = students.pop(index)

            return {
                "message": "Deleted student successfully",
                "data": deleted_student,
            }

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Student with id {student_id} not found",
    )


@app.put("/students/{student_id}", status_code=status.HTTP_200_OK)
async def update_student_by_id(
    student_id: int,
    updated_student: Student,
):
    for index, student in enumerate(students):
        if student.id == student_id:

            for existing_student in students:
                if (
                    existing_student.id == updated_student.id
                    and existing_student.id != student_id
                ):
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=(
                            f"Student with id "
                            f"{updated_student.id} already exists"
                        ),
                    )

            # Replace the student at the same List index
            students[index] = updated_student

            return {
                "message": "Updated student successfully",
                "data": updated_student,
            }

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Student with id {student_id} not found",
    )