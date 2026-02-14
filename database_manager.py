# database_manager.py - WITH PROPER CACHING IMPLEMENTED
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
        
        # Cache for faster lookups - NOW ACTUALLY USED!
        self._programs_cache = None
        self._colleges_cache = None
        
        # Load cache on initialization
        self._load_cache()
    
    # ========== CACHE MANAGEMENT ==========
    def _load_cache(self):
        """Load programs and colleges into cache on startup"""
        self._programs_cache = self.get_all_programs()
        self._colleges_cache = self.get_all_colleges()
        print(f"Cache loaded: {len(self._programs_cache)} programs, {len(self._colleges_cache)} colleges")
    
    def _refresh_cache(self):
        """Refresh the data cache - call this after adding/updating programs or colleges"""
        self._load_cache()
    
    def get_programs_cached(self):
        """Get programs from cache instead of reading file"""
        if self._programs_cache is None:
            self._load_cache()
        return self._programs_cache
    
    def get_colleges_cached(self):
        """Get colleges from cache instead of reading file"""
        if self._colleges_cache is None:
            self._load_cache()
        return self._colleges_cache
    
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
        NOW USES CACHE! 🚀
        """
        students = self.get_all_students()
        
        # ✅ USE CACHE instead of reading files
        programs = self.get_programs_cached()  # <-- CHANGED!
        colleges = self.get_colleges_cached()  # <-- CHANGED!
        
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
    
    def update_student(self, student_data):
        """
        Update an existing student's information
        
        Args:
            student_data: dict with keys: id, firstname, lastname, program_code, year, gender
        
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            # Read all students
            students = self.get_all_students()
            
            if not students:
                return False, "No students found in database"
            
            # Find and update the student
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
            
            # Write back to file
            with open(self.students_file, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['id', 'firstname', 'lastname', 'program_code', 'year', 'gender']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(students)
            
            return True, f"Student {student_data['firstname']} {student_data['lastname']} updated successfully!"
        
        except Exception as e:
            return False, f"Error updating student: {str(e)}"
    
    def delete_student(self, student_id):
        """
        Delete a student from the database
        
        Args:
            student_id: str - Student ID to delete
        
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            # Read all students
            students = self.get_all_students()
            
            if not students:
                return False, "No students found in database"
            
            # Find student name before deleting
            student_name = None
            original_count = len(students)
            
            for student in students:
                if student['id'] == student_id:
                    student_name = f"{student['firstname']} {student['lastname']}"
                    break
            
            # Filter out the student to delete
            students = [s for s in students if s['id'] != student_id]
            
            if len(students) == original_count:
                return False, f"Student with ID {student_id} not found"
            
            # Write back to file
            with open(self.students_file, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['id', 'firstname', 'lastname', 'program_code', 'year', 'gender']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                # Only write rows if there are students left
                if students:
                    writer.writerows(students)
            
            return True, f"Student {student_name} (ID: {student_id}) deleted successfully!"
        
        except Exception as e:
            return False, f"Error deleting student: {str(e)}"
    
    # ========== PROGRAM OPERATIONS ==========
    def get_all_programs(self):
        """Return all programs as list of dictionaries - READS FROM FILE"""
        programs = []
        if os.path.exists(self.programs_file):
            with open(self.programs_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    programs.append(row)
        return programs
    
    def get_program_by_code(self, code):
        """Get program by code - USES CACHE"""
        programs = self.get_programs_cached()  # <-- CHANGED!
        for program in programs:
            if program['code'] == code:
                return program
        return None
    
    def get_program_by_name(self, name):
        """Get program by name - USES CACHE"""
        programs = self.get_programs_cached()  # <-- CHANGED!
        for program in programs:
            if program['name'] == name:
                return program
        return None
    
    def get_program_display_list(self):
        """
        Get list of programs formatted for dropdown display
        Returns: List of dictionaries with display, code, name, college
        USES CACHE!
        """
        programs = self.get_programs_cached()  # <-- CHANGED!
        return DataLookup.get_program_display_list(programs)
    
    def program_exists(self, program_code):
        """Check if a program exists - USES CACHE"""
        return self.get_program_by_code(program_code) is not None
    
    def add_program(self, program_data):
        """Add a new program - DON'T FORGET TO REFRESH CACHE!"""
        programs = self.get_all_programs()
        programs.append(program_data)
        
        try:
            with open(self.programs_file, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['code', 'name', 'college']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(programs)
            
            # ✅ REFRESH CACHE after adding
            self._refresh_cache()
            
            return True, f"Program {program_data['code']} added successfully"
        except Exception as e:
            return False, f"Error saving program: {str(e)}"
    
    # ========== COLLEGE OPERATIONS ==========
    def get_all_colleges(self):
        """Return all colleges as list of dictionaries - READS FROM FILE"""
        colleges = []
        if os.path.exists(self.colleges_file):
            with open(self.colleges_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    colleges.append(row)
        return colleges
    
    def get_college_by_code(self, code):
        """Get college by code - USES CACHE"""
        colleges = self.get_colleges_cached()  # <-- CHANGED!
        for college in colleges:
            if college['code'] == code:
                return college
        return None
    
    def get_college_name(self, code):
        """Get college name from code - USES CACHE"""
        college = self.get_college_by_code(code)
        return college['name'] if college else code
    
    def add_college(self, college_data):
        """Add a new college - DON'T FORGET TO REFRESH CACHE!"""
        colleges = self.get_all_colleges()
        colleges.append(college_data)
        
        try:
            with open(self.colleges_file, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['code', 'name']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(colleges)
            
            # ✅ REFRESH CACHE after adding
            self._refresh_cache()
            
            return True, f"College {college_data['code']} added successfully"
        except Exception as e:
            return False, f"Error saving college: {str(e)}"