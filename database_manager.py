# database_manager.py
import csv
import os
from models import DataLookup  # Make sure this import is added

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
        self._init_students_file()
        self._init_programs_file()
        self._init_colleges_file()
        
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
            print(f"Created {self.students_file}")
    
    def _init_programs_file(self):
        """Create programs.csv with headers if it doesn't exist"""
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
            print(f"Created {self.programs_file} with sample data")
    
    def _init_colleges_file(self):
        """Create colleges.csv with headers if it doesn't exist"""
        if not os.path.exists(self.colleges_file):
            with open(self.colleges_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['code', 'name'])
                # Add sample data for testing
                writer.writerow(['CCS', 'College of Computer Studies'])
                writer.writerow(['COB', 'College of Business'])
                writer.writerow(['COE', 'College of Engineering'])
            print(f"Created {self.colleges_file} with sample data")
    
    # ========== CACHE MANAGEMENT ==========
    def _refresh_cache(self):
        """Refresh the data cache"""
        self._programs_cache = self.get_all_programs()
        self._colleges_cache = self.get_all_colleges()
    
    # ========== STUDENT OPERATIONS ==========
    def get_all_students(self):
        """Return all students as list of dictionaries"""
        students = []
        file_path = self.students_file
        print(f"\n=== DEBUG: Reading from {file_path} ===")
    
        if os.path.exists(file_path):
            print(f"File exists, size: {os.path.getsize(file_path)} bytes")
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    # Read raw content first
                    raw = f.read()
                    print(f"Raw content: {repr(raw[:200])}")
                    
                    # Reset and read as CSV
                    f.seek(0)
                    reader = csv.DictReader(f)
                    print(f"Fieldnames: {reader.fieldnames}")
                    
                    for i, row in enumerate(reader):
                        print(f"Row {i}: {row}")
                        students.append(row)
                        
                print(f"Total students read: {len(students)}")
            except Exception as e:
                print(f"Error reading file: {e}")
        else:
            print(f"File does not exist: {file_path}")
        
        return students
    
    def get_students_with_details(self):
        """
        Return all students with program names and college codes
        This is what you'll use for displaying in the table
        """
        students = self.get_all_students()
        programs = self.get_all_programs()
        colleges = self.get_all_colleges()
        
        detailed_students = []
        for student in students:
            # Make a copy and add display fields
            detailed = student.copy()
            
            # Get program code
            program_code = student['program_code']
            
            # Look up program name
            program_name = DataLookup.get_program_name_by_code(programs, program_code)
            detailed['program_name'] = program_name
            
            # Look up college code from program
            college_code = DataLookup.get_college_code_by_program(programs, program_code)
            detailed['college_code'] = college_code
            
            # Look up college name (optional - if you want full name instead of code)
            college_name = DataLookup.get_college_name_by_code(colleges, college_code)
            detailed['college_name'] = college_name
            
            detailed_students.append(detailed)
        
        return detailed_students
    
    def add_student(self, student_data):
        """
        Add a new student to CSV
        student_data: dict with keys: id, firstname, lastname, program_code, year, gender
        """
        print("\n" + "="*50)
        print("DB_MANAGER: add_student called")
        print("="*50)
        print(f"Student data received: {student_data}")
        print(f"File path: {os.path.abspath(self.students_file)}")
    
        # Get existing students
        students = self.get_all_students()
        print(f"Existing students count: {len(students)}")
        
        # Check for duplicate ID
        for student in students:
            if student['id'] == student_data['id']:
                print(f"Duplicate ID found: {student_data['id']}")
                return False, f"Student ID {student_data['id']} already exists"
        
        # Add new student
        students.append(student_data)
        print(f"Students after append: {len(students)}")
        
        # Save to CSV
        try:
            print("Attempting to write to CSV...")
            with open(self.students_file, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['id', 'firstname', 'lastname', 'program_code', 'year', 'gender']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(students)
                f.flush()
            print("Write completed successfully")
            
            # Verify
            if os.path.exists(self.students_file):
                size = os.path.getsize(self.students_file)
                print(f"File size after write: {size} bytes")
                
            return True, f"Student {student_data['id']} added successfully"
            
        except Exception as e:
            print(f"ERROR in add_student: {str(e)}")
            import traceback
            traceback.print_exc()
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
        print(f"DEBUG - Programs loaded: {len(programs)}")
        print(f"DEBUG - Program data: {programs}")
        return DataLookup.get_program_display_list(programs)
    
    def program_exists(self, program_code):
        """Check if a program exists"""
        program = self.get_program_by_code(program_code)
        return program is not None
    
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