# utils.py
import csv
import os

class CSVHandler:
    # Generic load function that replaces all your load_* functions
    @staticmethod
    def load_csv(filename):
        """Load any CSV file"""
        data = []
        if os.path.exists(filename):
            with open(filename, 'r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    data.append(row)
        return data
    
    # Generic save function that replaces save_students and others
    @staticmethod
    def save_csv(filename, data, fieldnames):
        """Save data to any CSV file"""
        with open(filename, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
    
    # Bonus: Get fieldnames from existing file
    @staticmethod
    def get_fieldnames(filename):
        """Read column names from CSV header"""
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                return next(reader, [])
        return []

# Keep your file constants here too
STUDENT_FILE = "students.csv"
PROGRAM_FILE = "programs.csv"
COLLEGE_FILE = "colleges.csv"