# database_manager.py
import csv
import os
from models import DataLookup


class DatabaseManager:
    """Handles all CSV file operations"""
    
    def __init__(self):
        # File paths
        self.students_file = 'data/students.csv'
        self.programs_file = 'data/programs.csv'
        self.colleges_file = 'data/colleges.csv'
        
        # Create data directory if it doesn't exist
        os.makedirs('data', exist_ok=True)
        
        # Initialize all CSV files
        """self._init_students_file()
        self._init_programs_file()
        self._init_colleges_file()"""
        
        # Cache for faster lookups
        self._programs_cache = None
        self._colleges_cache = None
    
    # ========== INITIALIZATION ==========
    def _init_students_file(self):
        """Create students.csv with headers if it doesn't exist"""
        if not os.path.exists(self.students_file):
            with open(self.students_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['id', 'firstname', 'lastname', 'program_code', 'year', 'gender'])
    
    def _init_programs_file(self):
        """Create programs.csv with headers and sample data if it doesn't exist"""
        if not os.path.exists(self.programs_file):
            with open(self.programs_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['code', 'name', 'college'])
                # Add sample data for testing
                writer.writerow(['BSCS', 'Bachelor of Science in Computer Science', 'CCS'])
                writer.writerow(['BSIT', 'Bachelor of Science in Information Technology', 'CCS'])
                writer.writerow(['BSBA', 'Bachelor of Science in Business Administration', 'COB'])
                writer.writerow(['BSEE', 'Bachelor of Science in Electrical Engineering', 'COE'])
                writer.writerow(['BSME', 'Bachelor of Science in Mechanical Engineering', 'COE'])
    
    def _init_colleges_file(self):
        """Create colleges.csv with headers and sample data if it doesn't exist"""
        if not os.path.exists(self.colleges_file):
            with open(self.colleges_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['code', 'name'])
                # Add sample data for testing
                writer.writerow(['CCS', 'College of Computer Studies'])
                writer.writerow(['COB', 'College of Business'])
                writer.writerow(['COE', 'College of Engineering'])
    
    # ========== CACHE MANAGEMENT ==========
    def _refresh_cache(self):
        """Refresh the data cache"""
        self._programs_cache = self.get_all_programs()
        self._colleges_cache = self.get_all_colleges()
    
    # ========== STUDENT OPERATIONS ==========
    def get_all_students(self):
        """Return all students as list of dictionaries"""
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
        """
        Return all students with program names and college codes
        Used for displaying in the table
        """
        students = self.get_all_students()
        programs = self.get_all_programs()
        colleges = self.get_all_colleges()
        
        detailed_students = []
        for student in students:
            detailed = student.copy()
            program_code = student['program_code']
            
            # Look up program name
            detailed['program_name'] = DataLookup.get_program_name_by_code(programs, program_code)
            
            # Look up college code from program
            detailed['college_code'] = DataLookup.get_college_code_by_program(programs, program_code)
            
            # Look up college name (optional)
            detailed['college_name'] = DataLookup.get_college_name_by_code(
                colleges, detailed['college_code']
            )
            
            detailed_students.append(detailed)
        
        return detailed_students
    
    def add_student(self, student_data):
        """
        Add a new student to CSV
        student_data: dict with keys: id, firstname, lastname, program_code, year, gender
        """
        # Get existing students
        students = self.get_all_students()
        
        # Check for duplicate ID
        for student in students:
            if student['id'] == student_data['id']:
                return False, f"Student ID {student_data['id']} already exists"
        
        # Add new student
        students.append(student_data)
        
        # Save to CSV
        try:
            with open(self.students_file, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['id', 'firstname', 'lastname', 'program_code', 'year', 'gender']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(students)
            
            return True, f"Student {student_data['id']} added successfully"
            
        except Exception as e:
            # Remove the student if save failed
            students.remove(student_data)
            return False, f"Error saving student: {str(e)}"
    
    # ========== PROGRAM OPERATIONS ==========
    def get_all_programs(self):
        """Return all programs as list of dictionaries"""
        programs = []
        if os.path.exists(self.programs_file):
            with open(self.programs_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    programs.append(row)
        return programs
    
    def get_program_by_code(self, code):
        """Get program by code"""
        programs = self.get_all_programs()
        for program in programs:
            if program['code'] == code:
                return program
        return None
    
    def get_program_by_name(self, name):
        """Get program by name"""
        programs = self.get_all_programs()
        for program in programs:
            if program['name'] == name:
                return program
        return None
    
    def get_program_display_list(self):
        """
        Get list of programs formatted for dropdown display
        Returns: List of dictionaries with display, code, name, college
        """
        programs = self.get_all_programs()
        return DataLookup.get_program_display_list(programs)
    
    def program_exists(self, program_code):
        """Check if a program exists"""
        return self.get_program_by_code(program_code) is not None
    
    # ========== COLLEGE OPERATIONS ==========
    def get_all_colleges(self):
        """Return all colleges as list of dictionaries"""
        colleges = []
        if os.path.exists(self.colleges_file):
            with open(self.colleges_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    colleges.append(row)
        return colleges
    
    def get_college_by_code(self, code):
        """Get college by code"""
        colleges = self.get_all_colleges()
        for college in colleges:
            if college['code'] == code:
                return college
        return None
    
    def get_college_name(self, code):
        """Get college name from code"""
        college = self.get_college_by_code(code)
        return college['name'] if college else code