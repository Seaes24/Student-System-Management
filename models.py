# models.py
import re
from datetime import datetime


class StudentValidator:
    """Validates student data according to requirements"""
    
    @staticmethod
    def validate_student_id(student_id):
        """Format: YYYY-NNNN (4 digits - 4 digits)"""
        if not student_id:
            return False, "Student ID is required"
        
        pattern = r'^\d{4}-\d{4}$'
        if not re.match(pattern, student_id):
            return False, "Student ID must be in format: YYYY-NNNN (e.g., 2024-0001)"
        
        # Check if year is reasonable
        year = int(student_id[:4])
        current_year = datetime.now().year
        if year < 2000 or year > current_year + 1:
            return False, f"Year must be between 2000 and {current_year + 1}"
        
        return True, "Valid"

    @staticmethod
    def validate_name(name, field_name):
        """Validate name fields"""
        if not name:
            return False, f"{field_name} is required"
        
        if len(name.strip()) < 2:
            return False, f"{field_name} must be at least 2 characters"
        
        if not name.replace(" ", "").isalpha():
            return False, f"{field_name} can only contain letters and spaces"
        
        return True, "Valid"
    
    @staticmethod
    def validate_year(year):
        """Validate year level (1-5)"""
        valid_years = ['1', '2', '3', '4', '5']
        if year not in valid_years:
            return False, "Year level must be 1, 2, 3, 4, or 5"
        return True, "Valid"
    
    @staticmethod
    def validate_gender(gender):
        """Validate gender"""
        valid_genders = ['Male', 'Female', 'M', 'F']
        if gender not in valid_genders:
            return False, "Gender must be Male, Female, M, or F"
        return True, "Valid"


class ProgramValidator:
    """Validates program data"""
    
    @staticmethod
    def validate_program_code(code):
        """Format: 3-5 uppercase letters, optional numbers"""
        if not code:
            return False, "Program code is required"
        pattern = r'^[A-Z]{3,5}\d{0,3}$'
        is_valid = bool(re.match(pattern, code))
        return is_valid, "Valid" if is_valid else "Invalid format"


class CollegeValidator:
    """Validates college data"""
    
    @staticmethod
    def validate_college_code(code):
        """Format: 2-5 uppercase letters"""
        if not code:
            return False, "College code is required"
        pattern = r'^[A-Z]{2,5}$'
        is_valid = bool(re.match(pattern, code))
        return is_valid, "Valid" if is_valid else "Invalid format"


class DataLookup:
    """Helper class for looking up related data"""
    
    @staticmethod
    def get_program_name_by_code(programs, code):
        """Get program name from program code"""
        if code == 'N/A':
            return 'N/A'
        
        for program in programs:
            if program['code'] == code:
                return program['name']
        
        return code  # Fallback to code if not found
    
    @staticmethod
    def get_program_code_by_name(programs, name):
        """Get program code from program name"""
        for program in programs:
            if program['name'] == name:
                return program['code']
        return None
    
    @staticmethod
    def get_college_code_by_program(programs, program_code):
        """Get college code from program code"""
        if program_code == 'N/A':
            return 'N/A'
        
        for program in programs:
            if program['code'] == program_code:
                return program['college']
        
        return 'N/A'
    
    @staticmethod
    def get_college_name_by_code(colleges, college_code):
        """Get college name from college code"""
        if college_code == 'N/A':
            return 'N/A'
        
        for college in colleges:
            if college['code'] == college_code:
                return college['name']
        
        return college_code  # Fallback to code if not found
    
    @staticmethod
    def get_program_display_list(programs):
        """
        Get list of programs formatted for dropdown display
        Returns: List of dictionaries with display, code, name, college
        """
        display_list = []
        
        for program in programs:
            # Format: "Program Name (College Code)"
            display_text = f"{program['name']} ({program['college']})"
            display_list.append({
                'display': display_text,
                'code': program['code'],
                'name': program['name'],
                'college': program['college']
            })
        
        # Sort by program name
        return sorted(display_list, key=lambda x: x['name'])