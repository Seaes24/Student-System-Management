import re
from datetime import datetime


class StudentValidator:
    
    @staticmethod
    def validate_student_id(student_id):
        if not student_id:
            return False, "Student ID is required"
        
        pattern = r'^\d{4}-\d{4}$'
        if not re.match(pattern, student_id):
            return False, "Student ID must be in format: YYYY-NNNN (e.g., 2024-0001)"
        
        year = int(student_id[:4])
        current_year = datetime.now().year
        if year < 2000 or year > current_year + 1:
            return False, f"Year must be between 2000 and {current_year + 1}"
        
        return True, "Valid"
    
    @staticmethod
    def validate_name(name, field_name):
        if not name:
            return False, f"{field_name} is required"
        
        if len(name.strip()) < 2:
            return False, f"{field_name} must be at least 2 characters"
        
        if not name.replace(" ", "").isalpha():
            return False, f"{field_name} can only contain letters and spaces"
        
        return True, "Valid"
    
    @staticmethod
    def validate_year(year):
        valid_years = ['1', '2', '3', '4', '5']
        if year not in valid_years:
            return False, "Year level must be 1, 2, 3, 4, or 5"
        return True, "Valid"
    
    @staticmethod
    def validate_gender(gender):
        valid_genders = ['Male', 'Female', 'M', 'F']
        if gender not in valid_genders:
            return False, "Gender must be Male, Female, M, or F"
        return True, "Valid"


class ProgramValidator:
    
    @staticmethod
    def validate_program_code(code):
        """Format: 4-10 uppercase letters also accepts 1 hyphen"""

        if not code:
            return False, "Program code is required"
        
        hyphen_count = code.count('-')
        
        if hyphen_count > 1:
            return False, "Only one hyphen allowed"
        
        letters_only = code.replace('-', '')
        
        if not letters_only.isalpha() or not letters_only.isupper():
            return False, "Only uppercase letters allowed (A-Z)"
        
        if not 4 <= len(letters_only) <= 10:
            return False, f"Must contain 4-10 letters (currently {len(letters_only)})"
        
        if hyphen_count == 1:
            if code.startswith('-') or code.endswith('-'):
                return False, "Hyphen cannot be at start or end"
        
        return True, "Valid"
    
    @staticmethod
    def validate_program_name(name):
        if not name:
            return False, "Program name is required"
        
        if not name.strip():
            return False, "Program name cannot be empty"
        
        name = ' '.join(name.split())
        
        if len(name) < 10:
            return False, "Program name is too short"
        if len(name) > 200:
            return False, "Program name is too long"
        
        lowercase_words = {
            'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from'
        }
        
        words = name.split()
        
        for i, word in enumerate(words):
            if not all(c.isalpha() or c in "'- " for c in word):
                return False, f"Invalid character in '{word}'"
            
            if i == 0:
                if not word[0].isupper():
                    return False, f"First word '{word}' must start with capital letter"
            else:
                if word.lower() in lowercase_words:
                    if word != word.lower():
                        return False, f"'{word}' should be lowercase"
                else:
                    if not word[0].isupper():
                        return False, f"'{word}' should start with capital letter"
        
        return True, "Valid program name"
    
    @staticmethod
    def check_duplicate_code(db_manager, code, current_code=None):
        all_programs = db_manager.get_all_programs()
        
        for program in all_programs:
            if program['code'] == code:
                if current_code and program['code'] == current_code:
                    continue
                else:
                    return False, f"Program code '{code}' already exists"
        
        return True, "Valid"
            

class CollegeValidator:
    
    @staticmethod
    def validate_college_code(code):
        """Format: 2-5 uppercase letters"""
        if not code:
            return False, "College code is required"
        pattern = r'^[A-Z]{2,5}$'
        is_valid = bool(re.match(pattern, code))
        return is_valid, "Valid" if is_valid else "Invalid format (use 2-5 uppercase letters)"
    
    @staticmethod
    def validate_college_name(name):
        """Validate college name"""
        if not name:
            return False, "College name is required"
        
        if not name.strip():
            return False, "College name cannot be empty"
        
        if len(name.strip()) < 3:
            return False, "College name must be at least 3 characters long"
        
        return True, "Valid"
    
    @staticmethod
    def check_duplicate_code(db_manager, code, current_code=None):
        all_colleges = db_manager.get_all_colleges()
        
        for college in all_colleges:
            if college['code'] == code:
                if current_code and college['code'] == current_code:
                    continue
                else:
                    return False, f"College code '{code}' already exists"
    
        return True, "Valid"


class DataLookup:
    
    @staticmethod
    def get_program_name_by_code(programs, code):
        if code == 'N/A' or not code:
            return 'N/A'
        
        for program in programs:
            if program['code'] == code:
                return program['name']
        
        return code
    
    @staticmethod
    def get_program_code_by_name(programs, name):
        if name == 'N/A' or not name:
            return 'N/A'
        
        for program in programs:
            if program['name'] == name:
                return program['code']
        return None
    
    @staticmethod
    def get_college_code_by_program(programs, program_code):
        if program_code == 'N/A' or not program_code:
            return 'N/A'
        
        for program in programs:
            if program['code'] == program_code:
                return program['college']
        
        return 'N/A'
    
    @staticmethod
    def get_college_name_by_code(colleges, college_code):
        if college_code == 'N/A' or not college_code:
            return 'N/A'
        
        for college in colleges:
            if college['code'] == college_code:
                return college['name']
        
        return college_code
    
    @staticmethod
    def get_program_display_list(programs):
        display_list = []
        
        for program in programs:
            college_display = program['college'] if program['college'] != 'N/A' else 'No College'
            display_text = f"{program['name']} ({college_display})"
            display_list.append({
                'display': display_text,
                'code': program['code'],
                'name': program['name'],
                'college': program['college']
            })
        
        return sorted(display_list, key=lambda x: x['name'])