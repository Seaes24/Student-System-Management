# diagnose_csv.py
import csv
import os

print("=" * 50)
print("CSV DIAGNOSTIC TOOL")
print("=" * 50)

# Check current directory
print(f"\n1. Current directory: {os.getcwd()}")
print(f"   Files in current folder: {[f for f in os.listdir('.') if f.endswith('.py')]}")

# Check data folder
data_path = 'data'
print(f"\n2. Data folder: {os.path.abspath(data_path)}")
print(f"   Exists? {os.path.exists(data_path)}")

if os.path.exists(data_path):
    print(f"   Files in data folder: {os.listdir(data_path)}")
else:
    print("   Creating data folder...")
    os.makedirs(data_path, exist_ok=True)

# Check programs.csv
prog_file = os.path.join(data_path, 'programs.csv')
print(f"\n3. Programs file: {os.path.abspath(prog_file)}")
print(f"   Exists? {os.path.exists(prog_file)}")

if os.path.exists(prog_file):
    print(f"   File size: {os.path.getsize(prog_file)} bytes")
    
    # Read raw content first
    print("\n   RAW FILE CONTENT (first 200 chars):")
    with open(prog_file, 'r', encoding='utf-8') as f:
        raw = f.read()
        print(f"   {repr(raw[:200])}")
    
    # Try reading as CSV with different methods
    print("\n   CSV READING ATTEMPTS:")
    
    # Method 1: csv.reader
    print("   Method 1 - csv.reader:")
    with open(prog_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)
        print(f"      Rows found: {len(rows)}")
        for i, row in enumerate(rows):
            print(f"      Row {i}: {row}")
    
    # Method 2: csv.DictReader
    print("\n   Method 2 - csv.DictReader:")
    with open(prog_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        print(f"      Fieldnames: {reader.fieldnames}")
        rows = list(reader)
        print(f"      Rows found: {len(rows)}")
        for i, row in enumerate(rows):
            print(f"      Row {i}: {row}")

# Check colleges.csv
col_file = os.path.join(data_path, 'colleges.csv')
print(f"\n4. Colleges file: {os.path.abspath(col_file)}")
print(f"   Exists? {os.path.exists(col_file)}")

if os.path.exists(col_file):
    print(f"   File size: {os.path.getsize(col_file)} bytes")
    
    print("\n   RAW FILE CONTENT (first 200 chars):")
    with open(col_file, 'r', encoding='utf-8') as f:
        raw = f.read()
        print(f"   {repr(raw[:200])}")
    
    print("\n   CSV READING ATTEMPTS:")
    with open(col_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)
        print(f"      Rows found: {len(rows)}")
        for i, row in enumerate(rows):
            print(f"      Row {i}: {row}")

print("\n" + "=" * 50)