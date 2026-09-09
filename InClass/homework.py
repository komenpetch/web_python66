from fastapi import FastAPI

app = FastAPI()

class Student(BaseModel):
    id: int
    name: str
    score: int

students = [
    {
        "id": 1,
        "name": "John Doe",
        "score": 20
    },
    {
        "id": 2,
        "name": "Jim Hanh",
        "score": 40
    },
    {
        "id": 3,
        "name": "Jack Gobert",
        "score": 55
    }
]

# Print all student
@app.get("/students")
async def get_students():
    return students

# Sum all student scores
@app.get("/students/sum")
async def sum_scores():
    total_score = sum(student["score"] for student in students)
    return {"total_score": total_score}

# Print student 1
@app.get("/students/{student_id}")
async def get_student(student_id: int):
    for student in students:
        if student["id"] == student_id:
            return student
    return {"error": "Student not found"}
