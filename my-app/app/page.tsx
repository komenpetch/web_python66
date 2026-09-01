"use client";

import { FormEvent, useEffect, useState } from "react";

type Student = {
  id: number;
  name: string;
  score: number;
};

const API_URL = "http://127.0.0.1:8000/students";

export default function Home() {
  const [students, setStudents] = useState<Student[]>([]);
  const [id, setId] = useState("");
  const [name, setName] = useState("");
  const [score, setScore] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(true);
  const [editingId, setEditingId] = useState<number | null>(null);

  // GET STUDENTS
  useEffect(() => {
    async function getStudents() {
      try {
        const response = await fetch(API_URL);

        if (!response.ok) {
          throw new Error("Failed to fetch students");
        }

        const result: Student[] = await response.json();
        setStudents(result);
      } catch (error) {
        console.error(error);
        setMessage("Failed to fetch students");
      } finally {
        setLoading(false);
      }
    }

    getStudents();
  }, []);

  // CLEAR FORM
  function clearForm() {
    setId("");
    setName("");
    setScore("");
    setEditingId(null);
  }

  // SELECT STUDENT FOR EDITING
  function editStudent(student: Student) {
    setEditingId(student.id);
    setId(String(student.id));
    setName(student.name);
    setScore(String(student.score));
    setMessage("");
  }

  // POST STUDENT
  async function addStudent() {
    const newStudent: Student = {
      id: Number(id),
      name,
      score: Number(score),
    };

    const response = await fetch(API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(newStudent),
    });

    const result = await response.json();

    if (!response.ok) {
      throw new Error(result.detail || "Failed to add student");
    }

    setStudents((currentStudents) => [
      ...currentStudents,
      result,
    ]);

    setMessage("Student added successfully");
    clearForm();
  }

// PUT STUDENT
async function updateStudent() {
  if (editingId === null) {
    return;
  }

  const updatedStudent: Student = {
    id: Number(id),
    name,
    score: Number(score),
  };

  const response = await fetch(`${API_URL}/${editingId}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(updatedStudent),
  });

  const result = await response.json();

  if (!response.ok) {
    throw new Error(result.detail || "Failed to update student");
  }

  const studentFromServer: Student = result.data;

  setStudents((currentStudents) =>
    currentStudents.map((student) =>
      student.id === editingId ? studentFromServer : student
    )
  );

  setMessage(result.message);
  clearForm();
}

  // SUBMIT FORM
  async function saveStudent(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setMessage("");

    try {
      if (editingId === null) {
        await addStudent();
      } else {
        await updateStudent();
      }
    } catch (error) {
      console.error(error);

      if (error instanceof Error) {
        setMessage(error.message);
      } else {
        setMessage("Failed to save student");
      }
    }
  }

  // DELETE STUDENT
  async function deleteStudent(studentId: number) {
    setMessage("");

    try {
      const response = await fetch(`API_URL/{studentId}`, {
        method: "DELETE",
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.detail || "Failed to delete student");
      }

      setStudents((currentStudents) =>
        currentStudents.filter((student) => student.id !== studentId)
      );

      if (editingId === studentId) {
        clearForm();
      }

      setMessage(result.message);
    } catch (error) {
      console.error(error);

      if (error instanceof Error) {
        setMessage(error.message);
      } else {
        setMessage("Failed to delete student");
      }
    }
  }

  return (
    <main className="p-8">
      <h1 className="mb-6 text-3xl font-bold">
        Hello, Students System
      </h1>

      <form onSubmit={saveStudent} className="mb-8 space-y-4">
        <h2 className="text-xl font-semibold">
          {editingId === null ? "Add Student" : "Edit Student"}
        </h2>

        <input
          type="number"
          placeholder="Student ID"
          value={id}
          onChange={(event) => setId(event.target.value)}
          required
          className="block w-full rounded border p-2"
        />

        <input
          type="text"
          placeholder="Student name"
          value={name}
          onChange={(event) => setName(event.target.value)}
          required
          className="block w-full rounded border p-2"
        />

        <input
          type="number"
          placeholder="Student score"
          value={score}
          onChange={(event) => setScore(event.target.value)}
          required
          className="block w-full rounded border p-2"
        />

        <button
          type="submit"
          className="rounded bg-blue-600 px-4 py-2 text-white"
        >
          {editingId === null ? "Add Student" : "Update Student"}
        </button>

        {editingId !== null && (
          <button
            type="button"
            onClick={clearForm}
            className="ml-2 rounded bg-gray-500 px-4 py-2 text-white"
          >
            Cancel
          </button>
        )}
      </form>

      {message && <p className="mb-4 text-green-600">{message}</p>}

      <h2 className="mb-3 text-xl font-semibold">Students</h2>

      {loading ? (
        <p>Loading students...</p>
      ) : (
        <ul className="space-y-3">
          {students.map((student) => (
            <li
              key={student.id}
              className="flex items-center justify-between rounded border p-3"
            >
              <span>
                {student.id}: {student.name}: {student.score}
              </span>

              <div>
                <button
                  type="button"
                  onClick={() => editStudent(student)}
                  className="mr-2 rounded bg-yellow-500 px-3 py-1 text-white"
                >
                  Edit
                </button>

                <button
                  type="button"
                  onClick={() => deleteStudent(student.id)}
                  className="rounded bg-red-600 px-3 py-1 text-white"
                >
                  Delete
                </button>
              </div>
            </li>
          ))}
        </ul>
      )}
    </main>
  );
}