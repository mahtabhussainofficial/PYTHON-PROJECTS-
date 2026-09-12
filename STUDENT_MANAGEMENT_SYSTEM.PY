import json
import os

FILE_NAME = "students_data.json"

# File Handling: Data load karna
def load_data():
    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, 'r') as file:
            return json.load(file)
    return [] # Agar file nahi hai to empty list return karega

# File Handling: Data save karna
def save_data(students):
    with open(FILE_NAME, 'w') as file:
        json.dump(students, file, indent=4)

# Grades calculate karna
def calculate_grade(marks):
    if marks >= 90: return 'A+'
    elif marks >= 80: return 'A'
    elif marks >= 70: return 'B'
    elif marks >= 60: return 'C'
    elif marks >= 50: return 'D'
    else: return 'Fail'

# 1. Add Student
def add_student(students):
    roll_no = input("Enter Roll Number: ")
    
    # Check if student already exists
    for s in students:
        if s['roll_no'] == roll_no:
            print("Error: Student with this Roll Number already exists!")
            return

    name = input("Enter Student Name: ")
    marks = float(input("Enter Marks (out of 100): "))
    grade = calculate_grade(marks)

    # Dictionary bana kar list mein add karna
    student = {"roll_no": roll_no, "name": name, "marks": marks, "grade": grade}
    students.append(student)
    
    save_data(students) # Data file mein save karna
    print(f"Student '{name}' added successfully! Grade: {grade}")

# 2. View All Students
def view_students(students):
    if not students:
        print("No students found in the database!")
        return
        
    print("\n--- All Students ---")
    for s in students:
        print(f"Roll No: {s['roll_no']} | Name: {s['name']} | Marks: {s['marks']} | Grade: {s['grade']}")
    print("------------------------\n")

# 3. Search Student
def search_student(students):
    roll_no = input("Enter Roll No to search: ")
    for s in students:
        if s['roll_no'] == roll_no:
            print(f"\nFound! Roll No: {s['roll_no']} | Name: {s['name']} | Marks: {s['marks']} | Grade: {s['grade']}\n")
            return
    print("Student not found!")

# 4. Update Student
def update_student(students):
    roll_no = input("Enter Roll No to update: ")
    for s in students:
        if s['roll_no'] == roll_no:
            print(f"Current Name: {s['name']}, Current Marks: {s['marks']}")
            s['name'] = input("Enter New Name: ")
            s['marks'] = float(input("Enter New Marks: "))
            s['grade'] = calculate_grade(s['marks'])
            
            save_data(students)
            print("Student updated successfully!")
            return
    print("Student not found!")

# 5. Delete Student
def delete_student(students):
    roll_no = input("Enter Roll No to delete: ")
    for i in range(len(students)):
        if students[i]['roll_no'] == roll_no:
            del students[i]
            save_data(students)
            print("Student deleted successfully!")
            return
    print("Student not found!")

# Main Menu Logic
def main():
    students = load_data()
    
    while True:
        print("\n===Student Management System ===")
        print("1. Add Student")
        print("2. View All Students")
        print("3. Search Student")
        print("4. Update Student")
        print("5. Delete Student")
        print("6. Exit")

        choice = input("Enter your choice (1-6): ")

        if choice == '1': 
            add_student(students)
        elif choice == '2': 
            view_students(students)
        elif choice == '3': 
            search_student(students)
        elif choice == '4': 
            update_student(students)
        elif choice == '5': 
            delete_student(students)
        elif choice == '6':
            print("Exiting Program. Khuda Hafiz! 👋")
            break
        else:
            print("Invalid choice! Please select between 1 and 6.")

# Program yahan se start hota hai
if __name__ == "__main__":
    main()