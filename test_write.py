# test_write.py
import csv
import os

test_file = 'data/students.csv'
test_data = [
    {'id': '2024-9999', 'firstname': 'Test', 'lastname': 'User', 
     'program_code': 'BSCS', 'year': '1', 'gender': 'Male'}
]

print(f"Current directory: {os.getcwd()}")
print(f"Absolute path: {os.path.abspath(test_file)}")

try:
    with open(test_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['id', 'firstname', 'lastname', 'program_code', 'year', 'gender']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(test_data)
        f.flush()
    print("Write successful!")
    
    # Verify
    with open(test_file, 'r') as f:
        print("File contains:")
        print(f.read())
except Exception as e:
    print(f"Error: {e}")