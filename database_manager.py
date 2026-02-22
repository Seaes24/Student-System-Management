import csv
import os
from models import DataLookup


class DatabaseManager:
    """Handles all CSV file operations"""
    
    def __init__(self):
        self.students_file = 'data/students.csv'
        self.programs_file = 'data/programs.csv'
        self.colleges_file = 'data/colleges.csv'
        
        os.makedirs('data', exist_ok=True)
        
        self._programs_cache = None
        self._colleges_cache = None
        

        self._load_cache()
    
    # ========== CACHE MANAGEMENT ==========
    def _load_cache(self):
        self._programs_cache = self.get_all_programs()
        self._colleges_cache = self.get_all_colleges()
        print(f"Cache loaded: {len(self._programs_cache)} programs, {len(self._colleges_cache)} colleges")
    
    def _refresh_cache(self):
        self._load_cache()
    
    def get_programs_cached(self):
        if self._programs_cache is None:
            self._load_cache()
        return self._programs_cache
    
    def get_colleges_cached(self):
        if self._colleges_cache is None:
            self._load_cache()
        return self._colleges_cache
    
    # ========== INITIALIZATION ==========
    def _init_students_file(self):
        if not os.path.exists(self.students_file):
            with open(self.students_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['id', 'firstname', 'lastname', 'program_code', 'year', 'gender'])
    
    def _init_programs_file(self):
        if not os.path.exists(self.programs_file):
            with open(self.programs_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['code', 'name', 'college'])
                writer.writerow(['BSCS', 'Bachelor of Science in Computer Science', 'CCS'])
                writer.writerow(['BSIT', 'Bachelor of Science in Information Technology', 'CCS'])
                writer.writerow(['BSBA', 'Bachelor of Science in Business Administration', 'COB'])
                writer.writerow(['BSEE', 'Bachelor of Science in Electrical Engineering', 'COE'])
                writer.writerow(['BSME', 'Bachelor of Science in Mechanical Engineering', 'COE'])
    
    def _init_colleges_file(self):
        if not os.path.exists(self.colleges_file):
            with open(self.colleges_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['code', 'name'])
                writer.writerow(['CCS', 'College of Computer Studies'])
                writer.writerow(['COB', 'College of Business'])
                writer.writerow(['COE', 'College of Engineering'])
    
    # ========== STUDENT OPERATIONS ==========
    def get_all_students(self):
        students = []
        if os.path.exists(self.students_file):
            try:
                with open(self.students_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        students.append(row)
            except Exception as e:
                print(f"Error reading students file: {e}")
        return students
    
    def get_students_with_details(self):
        students = self.get_all_students()
        
        programs = self.get_programs_cached() 
        colleges = self.get_colleges_cached() 
        
        detailed_students = []
        for student in students:
            detailed = student.copy()
            program_code = student['program_code']
            
            detailed['program_name'] = DataLookup.get_program_name_by_code(programs, program_code)
            
            detailed['college_code'] = DataLookup.get_college_code_by_program(programs, program_code)
            
            detailed['college_name'] = DataLookup.get_college_name_by_code(
                colleges, detailed['college_code']
            )
            
            detailed_students.append(detailed)
        
        return detailed_students
    
    def add_student(self, student_data):
        students = self.get_all_students()
        
        for student in students:
            if student['id'] == student_data['id']:
                return False, f"Student ID {student_data['id']} already exists"
        
        students.append(student_data)
        
        try:
            with open(self.students_file, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['id', 'firstname', 'lastname', 'program_code', 'year', 'gender']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(students)
            
            return True, f"Student {student_data['id']} added successfully"
            
        except Exception as e:
            students.remove(student_data)
            return False, f"Error saving student: {str(e)}"
    
    def update_student(self, student_data):
        try:
            students = self.get_all_students()
            
            if not students:
                return False, "No students found in database"
            
            student_found = False
            for i, student in enumerate(students):
                if student['id'] == student_data['id']:
                    students[i] = {
                        'id': student_data['id'],
                        'firstname': student_data['firstname'],
                        'lastname': student_data['lastname'],
                        'program_code': student_data['program_code'],
                        'year': student_data['year'],
                        'gender': student_data['gender']
                    }
                    student_found = True
                    break
            
            if not student_found:
                return False, f"Student with ID {student_data['id']} not found"
            
            with open(self.students_file, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['id', 'firstname', 'lastname', 'program_code', 'year', 'gender']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(students)
            
            return True, f"Student {student_data['firstname']} {student_data['lastname']} updated successfully!"
        
        except Exception as e:
            return False, f"Error updating student: {str(e)}"
    
    def delete_student(self, student_id):
        try:
            students = self.get_all_students()
            
            if not students:
                return False, "No students found in database"
            
    
            student_name = None
            original_count = len(students)
            
            for student in students:
                if student['id'] == student_id:
                    student_name = f"{student['firstname']} {student['lastname']}"
                    break
            
            students = [s for s in students if s['id'] != student_id]
            
            if len(students) == original_count:
                return False, f"Student with ID {student_id} not found"
            
            with open(self.students_file, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['id', 'firstname', 'lastname', 'program_code', 'year', 'gender']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                if students:
                    writer.writerows(students)
            
            return True, f"Student {student_name} (ID: {student_id}) deleted successfully!"
        
        except Exception as e:
            return False, f"Error deleting student: {str(e)}"
    # ========== PROGRAM OPERATIONS ==========
    def get_all_programs(self):
            if self._programs_cache is None:
                programs = []
                if os.path.exists(self.programs_file):
                    with open(self.programs_file, 'r', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            programs.append(row)
                self._programs_cache = programs
            
            return self._programs_cache
        
    def get_program_by_code(self, code):
        programs = self.get_programs_cached()  
        for program in programs:
            if program['code'] == code:
                return program
        return None
    
    def get_program_by_name(self, name):
        programs = self.get_programs_cached() 
        for program in programs:
            if program['name'] == name:
                return program
        return None
    
    def get_program_display_list(self):
        programs = self.get_programs_cached()
        return DataLookup.get_program_display_list(programs)
    
    def program_exists(self, program_code):
        return self.get_program_by_code(program_code) is not None
    
    def add_program(self, program_data):
        programs = self.get_all_programs()

        for program in programs: 
            if program['code'] == program_data['code']:
                return False, f"Program code {program_data['code']} already exists"
            
        programs.append(program_data)
        
        try:
            with open(self.programs_file, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['code', 'name', 'college']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(programs)
            
            self._refresh_cache()
            
            return True, f"Program {program_data['code']} added successfully"
        except Exception as e:
            return False, f"Error saving program: {str(e)}"
    
    def update_program(self, program_data, old_code=None):
        try:
            programs = self.get_all_programs()
            
            if not programs:
                return False, "No programs found in database"
            
            search_code = old_code if old_code else program_data['code']
            program_found = False
            
            for i, program in enumerate(programs):
                if program['code'] == search_code:
                    programs[i] = {
                        'code': program_data['code'],
                        'name': program_data['name'],
                        'college': program_data['college']
                    }
                    program_found = True
                    break
            
            if not program_found:
                return False, f"Program with code {search_code} not found"
            
            students_updated = 0
            if old_code and old_code != program_data['code']:
                students = self.get_all_students()
                
                for student in students:
                    if student['program_code'] == old_code:
                        student['program_code'] = program_data['code']
                        students_updated += 1
                
                if students_updated > 0:
                    with open(self.students_file, 'w', newline='', encoding='utf-8') as f:
                        fieldnames = ['id', 'firstname', 'lastname', 'program_code', 'year', 'gender']
                        writer = csv.DictWriter(f, fieldnames=fieldnames)
                        writer.writeheader()
                        writer.writerows(students)
            
            with open(self.programs_file, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['code', 'name', 'college']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(programs)
            
            self._refresh_cache()
            
            message = f"Program {program_data['name']} updated successfully!"
            if students_updated > 0:
                message += f"\n{students_updated} student(s) updated to new program code."
            
            return True, message
        
        except Exception as e:
            return False, f"Error updating program: {str(e)}"

    def delete_program(self, program_code):
        try:
            students = self.get_all_students()
            students_updated = 0
            
            for student in students:
                if student['program_code'] == program_code:
                    student['program_code'] = 'N/A'
                    students_updated += 1
            
            if students_updated > 0:
                with open(self.students_file, 'w', newline='', encoding='utf-8') as f:
                    fieldnames = ['id', 'firstname', 'lastname', 'program_code', 'year', 'gender']
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(students)
            
            programs = self.get_all_programs()
            
            if not programs:
                return False, "No programs found in database"
            
            program_name = None
            original_count = len(programs)
            
            for program in programs:
                if program['code'] == program_code:
                    program_name = program['name']
                    break
            
            programs = [p for p in programs if p['code'] != program_code]
            
            if len(programs) == original_count:
                return False, f"Program with code {program_code} not found"
            
            with open(self.programs_file, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['code', 'name', 'college']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                if programs:
                    writer.writerows(programs)
            
            self._refresh_cache()
            
            message = f"Program {program_name} ({program_code}) deleted successfully!"
            if students_updated > 0:
                message += f"\n{students_updated} student(s) were updated to have 'N/A' as their program."
            
            return True, message
        
        except Exception as e:
            return False, f"Error deleting program: {str(e)}"
        
    
    # ========== COLLEGE OPERATIONS ==========
    def get_all_colleges(self):
        colleges = []
        if os.path.exists(self.colleges_file):
            with open(self.colleges_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    colleges.append(row)
        return colleges
    
    def get_college_by_code(self, code):
        colleges = self.get_colleges_cached()
        for college in colleges:
            if college['code'] == code:
                return college
        return None
    
    def get_college_name(self, code):
        college = self.get_college_by_code(code)
        return college['name'] if college else code
    
    def add_college(self, college_data):
        colleges = self.get_all_colleges()
        
        for college in colleges: 
            if college['code'] == college_data['code']: 
                return False, f"College code {college_data['code']} already exists"  
            
        colleges.append(college_data)

        try:
            with open(self.colleges_file, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['code', 'name']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(colleges)
            
            self._refresh_cache()
            
            return True, f"College {college_data['code']} added successfully"
        except Exception as e:
            return False, f"Error saving college: {str(e)}"
    
    def update_college(self, college_data, old_code=None):
        
        try:
            colleges = self.get_all_colleges()
            
            if not colleges:
                return False, "No colleges found in database"
            
            search_code = old_code if old_code else college_data['code']
            college_found = False
            programs_updated = 0
            
            for i, college in enumerate(colleges):
                if college['code'] == search_code:
                    colleges[i] = {
                        'code': college_data['code'],
                        'name': college_data['name']
                    }
                    college_found = True
                    break
            
            if not college_found:
                return False, f"College with code {search_code} not found"
            
            if old_code and old_code != college_data['code']:
                programs = self.get_all_programs()
                programs_updated = 0
                
                for program in programs:
                    if program['college'] == old_code:
                        program['college'] = college_data['code']
                        programs_updated += 1
                
                if programs_updated > 0:
                    with open(self.programs_file, 'w', newline='', encoding='utf-8') as f:
                        fieldnames = ['code', 'name', 'college']
                        writer = csv.DictWriter(f, fieldnames=fieldnames)
                        writer.writeheader()
                        writer.writerows(programs)
            
            with open(self.colleges_file, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['code', 'name']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(colleges)
            
            self._colleges_cache = None
            
            message = f"College {college_data['name']} updated successfully!"
            if old_code and old_code != college_data['code']:
                if programs_updated > 0:
                    message += f"\n{programs_updated} program(s) updated to use new college code."
            
            return True, message
        
        except Exception as e:
            return False, f"Error updating college: {str(e)}"

    def delete_college(self, college_code):
        try:
            programs = self.get_all_programs()
            programs_updated = 0
            
            for program in programs:
                if program['college'] == college_code:
                    program['college'] = 'N/A'
                    programs_updated += 1
            
            if programs_updated > 0:
                with open(self.programs_file, 'w', newline='', encoding='utf-8') as f:
                    fieldnames = ['code', 'name', 'college']
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(programs)
            
            colleges = self.get_all_colleges()
            
            if not colleges:
                return False, "No colleges found in database"
            
            college_name = None
            original_count = len(colleges)
            
            for college in colleges:
                if college['code'] == college_code:
                    college_name = college['name']
                    break
            
            colleges = [c for c in colleges if c['code'] != college_code]
            
            if len(colleges) == original_count:
                return False, f"College with code {college_code} not found"
            
            with open(self.colleges_file, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['code', 'name']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                if colleges:
                    writer.writerows(colleges)
            
            self._refresh_cache()
            
            message = f"College {college_name} (Code: {college_code}) deleted successfully!"
            if programs_updated > 0:
                message += f"\n{programs_updated} program(s) were updated to have 'N/A' as their college."
            
            return True, message
        
        except Exception as e:
            return False, f"Error deleting college: {str(e)}"