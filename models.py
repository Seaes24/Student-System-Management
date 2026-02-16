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
        """Format: 4-10 uppercase letters also accepts 1 hyphen"""

        if not code:
            return False, "Program code is required"
        
        # Count hyphens
        hyphen_count = code.count('-')
        
        # Check for exactly 0 or 1 hyphen
        if hyphen_count > 1:
            return False, "Only one hyphen allowed"
        
        # Remove hyphen for letter count validation
        letters_only = code.replace('-', '')
        
        # Check if all remaining chars are uppercase letters
        if not letters_only.isalpha() or not letters_only.isupper():
            return False, "Only uppercase letters allowed (A-Z)"
        
        # Check letter count (excluding hyphen)
        if not 4 <= len(letters_only) <= 10:
            return False, f"Must contain 4-10 letters (currently {len(letters_only)})"
        
        # Check hyphen position (optional - not at start or end)
        if hyphen_count == 1:
            if code.startswith('-') or code.endswith('-'):
                return False, "Hyphen cannot be at start or end"
        
        return True, "Valid"
    
    @staticmethod
    def validate_program_name(name):
        """Format for program name"""
        if not name:
            return False, "Program name is required"
        
        if not name.strip():
            return False, "Program name cannot be empty"
        
        # Remove extra spaces and trim
        name = ' '.join(name.split())
        
        # Check length
        if len(name) < 10:
            return False, "Program name is too short"
        if len(name) > 200:
            return False, "Program name is too long"
        
        # Words that should remain lowercase (unless at start)
        lowercase_words = {
            'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from'
        }
        
        # Split into words
        words = name.split()
        
        # Check each word
        for i, word in enumerate(words):
            # Check for invalid characters (only letters, spaces, hyphens, apostrophes allowed)
            if not all(c.isalpha() or c in "'- " for c in word):
                return False, f"Invalid character in '{word}'"
            
            # First word must be capitalized
            if i == 0:
                if not word[0].isupper():
                    return False, f"First word '{word}' must start with capital letter"
            else:
                # Check if word should be lowercase
                if word.lower() in lowercase_words:
                    if word != word.lower():
                        return False, f"'{word}' should be lowercase"
                else:
                    # Regular words should be capitalized (first letter capital)
                    if not word[0].isupper():
                        return False, f"'{word}' should start with capital letter"
        
        return True, "Valid program name"
            

class CollegeValidator:
    """Validates college data"""
    
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
        """
        Check if college code already exists
        Args:
            code: The new code to check
            current_code: The current code of the college being edited (if editing)
        """
        # Get all colleges from database
        all_colleges = db_manager.get_all_colleges()
        
        for college in all_colleges:
            if college['code'] == code:
                # Found a match
                if current_code and college['code'] == current_code:
                    # This is the same college being edited - OK
                    continue
                else:
                    # Different college has this code - DUPLICATE!
                    return False, f"College code '{code}' already exists"
    
        return True, "Valid"


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