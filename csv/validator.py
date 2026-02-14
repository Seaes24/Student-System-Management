import re

class Validators:
    @staticmethod
    def validate_student_id(student_id):
        """Format: YYYY-NNNN (4 digits - 4 digits)"""
        pattern = r'^\d{4}-\d{4}$'
        return bool(re.match(pattern, student_id))
    
    @staticmethod
    def validate_name(name):
        """Only letters, spaces, and common name characters"""
        pattern = r'^[A-Za-z\s\'-]+$'
        return bool(re.match(pattern, name)) and len(name) >= 2
    
    @staticmethod
    def validate_course_code(course_code):
        """Format: 3-5 uppercase letters followed by optional 2-3 numbers"""
        pattern = r'^[A-Z]{3,5}\d{0,3}$'
        return bool(re.match(pattern, course_code))
    
    @staticmethod
    def validate_college_code(college_code):
        """Format: 2-5 uppercase letters"""
        pattern = r'^[A-Z]{2,5}$'
        return bool(re.match(pattern, college_code))
    
    @staticmethod
    def validate_gender(gender):
        return gender.lower() in ['male', 'female', 'm', 'f']
    
    @staticmethod
    def validate_year_level(year):
        return str(year) in ['1', '2', '3', '4', '5']