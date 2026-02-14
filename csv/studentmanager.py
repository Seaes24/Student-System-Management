import re
import dloader


def create_student(student):
    students = dloader.load_students()
    programs = dloader.load_programs()

    # Validate ID format YYYY-NNNN
    if not re.match(r"^\d{4}-\d{4}$", student["id"]):
        return False, "Invalid ID format (YYYY-NNNN)"

    # Check duplicate ID
    for s in students:
        if s["id"] == student["id"]:
            return False, "Student ID already exists"

    # Check program exists
    program_codes = [p["code"] for p in programs]
    if student["program_code"] not in program_codes:
        return False, "Program does not exist"

    # Add student
    students.append(student)
    dloader.save_students(students)

    return True, "Student added successfully"

def get_all_students():
    students = dloader.load_students()
    programs = dloader.load_programs()

    # Map program code → program data
    program_map = {p["code"]: p for p in programs}

    result = []

    for s in students:
        program = program_map.get(s["program_code"], {})

        result.append({
            "id": s["id"],
            "firstname": s["firstname"],
            "lastname": s["lastname"],
            "program_code": s["program_code"],
            "year": s["year"],
            "gender": s["gender"]
        })

    return result