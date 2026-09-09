students = [1,2,3,4,"CoC"]

students[3] = "CoC"

students.extend(["end1", "end2"])
#students.append("end3")
#students.append("end4")

students.insert(1, "New Value")
print(students)
#students.remove("New Value")
#print(students)
students.pop(1)
students.pop()
print(students)

if "CoC" in students:
    print("IN")
    
print(f"CoC is at index: {students.index('CoC')}")

print(students.count("CoC"))

number = [1,22,3,4]
number.sort()
print(number)

print(sorted(number))
print(number)