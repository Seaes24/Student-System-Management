# mainqt.py - UPDATED with Program Names Dropdown and College Auto-Display
from PyQt6 import uic
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTableWidgetItem, 
                             QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QComboBox, QPushButton, QMessageBox,
                             QRadioButton, QButtonGroup, QCompleter)
from PyQt6.QtCore import Qt
import sys
from database_manager import DatabaseManager
from models import StudentValidator, DataLookup  # Added DataLookup import

class AddStudentDialog(QDialog):
    """Dialog for adding a new student - Shows PROGRAM NAMES in dropdown"""
    
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.setWindowTitle("Add New Student")
        self.setModal(True)
        self.setMinimumWidth(500)  # Wider to show full program names
        
        # Get programs for dropdown (formatted for display with college codes)
        self.program_display_list = self.db_manager.get_program_display_list()
        print(f"DEBUG - Got {len(self.program_display_list)} display items")  # Add this
        
        # Main layout
        layout = QVBoxLayout()
        
        # ========== FORM FIELDS ==========
        
        # 1. Student ID
        id_layout = QHBoxLayout()
        id_layout.addWidget(QLabel("Student ID (YYYY-NNNN):*"))
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("2024-0001")
        id_layout.addWidget(self.id_input)
        layout.addLayout(id_layout)
        
        # 2. First Name
        firstname_layout = QHBoxLayout()
        firstname_layout.addWidget(QLabel("First Name:*"))
        self.firstname_input = QLineEdit()
        self.firstname_input.setPlaceholderText("John")
        firstname_layout.addWidget(self.firstname_input)
        layout.addLayout(firstname_layout)
        
        # 3. Last Name
        lastname_layout = QHBoxLayout()
        lastname_layout.addWidget(QLabel("Last Name:*"))
        self.lastname_input = QLineEdit()
        self.lastname_input.setPlaceholderText("Smith")
        lastname_layout.addWidget(self.lastname_input)
        layout.addLayout(lastname_layout)
        
        # 4. Program Name - COMBOBOX WITH PROGRAM NAMES (AUTO-COMPLETE)
        program_layout = QHBoxLayout()
        program_layout.addWidget(QLabel("Program Name:*"))
        
        self.program_combo = QComboBox()
        self.program_combo.setEditable(True)
        self.program_combo.setMinimumWidth(350)
        
        # Add program names to dropdown (formatted with college code)
        display_texts = [item['display'] for item in self.program_display_list]
        print(f"DEBUG - Display texts: {display_texts}") 
        self.program_combo.addItems(display_texts)
        
        # Set up auto-complete
        self.completer = QCompleter(display_texts)
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchFlag.MatchContains)  # Contains text, not just starts with
        self.completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.program_combo.setCompleter(self.completer)
        
        # Store the full program data for lookup
        self.program_data = {item['display']: item for item in self.program_display_list}
        
        program_layout.addWidget(self.program_combo)
        layout.addLayout(program_layout)
        
        # 5. Year Level
        year_layout = QHBoxLayout()
        year_layout.addWidget(QLabel("Year Level:*"))
        self.year_combo = QComboBox()
        self.year_combo.addItems(['1', '2', '3', '4', '5'])
        year_layout.addWidget(self.year_combo)
        layout.addLayout(year_layout)
        
        # 6. Gender (Radio Buttons)
        gender_layout = QHBoxLayout()
        gender_layout.addWidget(QLabel("Gender:*"))
        
        self.gender_group = QButtonGroup(self)
        self.male_radio = QRadioButton("Male")
        self.female_radio = QRadioButton("Female")
        
        self.gender_group.addButton(self.male_radio)
        self.gender_group.addButton(self.female_radio)
        
        gender_layout.addWidget(self.male_radio)
        gender_layout.addWidget(self.female_radio)
        self.male_radio.setChecked(True)  # Default to Male
        
        layout.addLayout(gender_layout)
        
        # Add some spacing
        layout.addSpacing(20)
        
        # ========== BUTTONS ==========
        button_layout = QHBoxLayout()
        
        self.save_button = QPushButton("Save Student")
        self.save_button.clicked.connect(self.save_student)
        self.save_button.setDefault(True)
        button_layout.addWidget(self.save_button)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        # Set the layout
        self.setLayout(layout)
        
        # Set focus to first input
        self.id_input.setFocus()
    
    def get_selected_program_code(self):
        """Extract the program code from the selected display text"""
        selected_text = self.program_combo.currentText().strip()
        
        # Check if it's exactly one of our display items
        if selected_text in self.program_data:
            return self.program_data[selected_text]['code']
        
        # If not, try to find by partial match
        for display, data in self.program_data.items():
            if selected_text.lower() in display.lower():
                return data['code']
        
        return None
    
    def save_student(self):
        """Validate and save the student"""
        
        print("\n" + "="*50)
        print("DIALOG: save_student called")
        print("="*50)

        
        # === GET DATA FROM FORM ===
        selected_program_code = self.get_selected_program_code()
        print(f"Selected program code: {selected_program_code}")
        
        student_data = {
            'id': self.id_input.text().strip(),
            'firstname': self.firstname_input.text().strip(),
            'lastname': self.lastname_input.text().strip(),
            'program_code': selected_program_code,
            'year': self.year_combo.currentText(),
            'gender': 'Male' if self.male_radio.isChecked() else 'Female'
        }

        print(f"Student data prepared: {student_data}")
        
        # === VALIDATION ===
        
        # 1. Validate Student ID
        valid, message = StudentValidator.validate_student_id(student_data['id'])
        if not valid:
            QMessageBox.warning(self, "Validation Error", message)
            self.id_input.setFocus()
            return
        
        # 2. Validate First Name
        valid, message = StudentValidator.validate_name(student_data['firstname'], "First Name")
        if not valid:
            QMessageBox.warning(self, "Validation Error", message)
            self.firstname_input.setFocus()
            return
        
        # 3. Validate Last Name
        valid, message = StudentValidator.validate_name(student_data['lastname'], "Last Name")
        if not valid:
            QMessageBox.warning(self, "Validation Error", message)
            self.lastname_input.setFocus()
            return
        
        # 4. Validate Program Selection
        if not student_data['program_code']:
            QMessageBox.warning(self, "Validation Error", 
                              "Please select a valid program from the list")
            self.program_combo.setFocus()
            return
        
        # Check if program exists in database
        if not self.db_manager.program_exists(student_data['program_code']):
            QMessageBox.warning(self, "Validation Error", 
                              f"Program '{self.program_combo.currentText()}' does not exist.\n"
                              "Please select a program from the list.")
            self.program_combo.setFocus()
            return
        
        # 5. Validate Year
        valid, message = StudentValidator.validate_year(student_data['year'])
        if not valid:
            QMessageBox.warning(self, "Validation Error", message)
            return
        
        # === CONFIRMATION DIALOG ===
        # Get program name for display
        program_display = self.program_combo.currentText()
        
        confirm_msg = (
            f"Are you sure you want to add this student?\n\n"
            f"Student ID: {student_data['id']}\n"
            f"Name: {student_data['lastname']}, {student_data['firstname']}\n"
            f"Program: {program_display}\n"
            f"Year: {student_data['year']}\n"
            f"Gender: {student_data['gender']}"
        )
        
        reply = QMessageBox.question(
            self, 
            "Confirm Addition",
            confirm_msg,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            print("User confirmed - calling db_manager.add_student()")

            # === SAVE TO DATABASE ===
            success, message = self.db_manager.add_student(student_data)
            print(f"add_student returned: success={success}, message={message}")
            
            if success:
                print("Success - accepting dialog")
                QMessageBox.information(self, "Success", message)
                self.accept()  # Close dialog with success
            else:
                print(f"Error - showing message: {message}")
                QMessageBox.critical(self, "Error", message)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Load the .ui file
        uic.loadUi('main_window.ui', self)
        
        # Initialize database manager
        self.db_manager = DatabaseManager()
        
        # Connect buttons - USING YOUR EXACT OBJECT NAMES
        self.studentsButton.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0))
        self.programsButton.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(1))
        self.collegesButton.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(2))
        
        # Connect Add Student button - USING YOUR EXACT OBJECT NAME
        self.addStudentButton.clicked.connect(self.open_add_student_dialog)
        
        # Load initial data into table
        self.load_students_table()
    
    def open_add_student_dialog(self):
        """Open the Add Student dialog"""
        dialog = AddStudentDialog(self.db_manager, self)
        
        # If dialog is accepted (user clicked Save and it was successful)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_students_table()  # Refresh the table
    
    def load_students_table(self):
        """Load students from database into the table - SHOWING PROGRAM NAMES AND COLLEGE CODES"""
        # Get your table widget - USING YOUR EXACT OBJECT NAME
        table = self.dataTableStudents
        
        # Clear existing rows
        table.setRowCount(0)
        
        # Get students with detailed information (includes program_name and college_code)
        students = self.db_manager.get_students_with_details()
        
        # Set row count
        table.setRowCount(len(students))
        
        # Set column headers - ADD COLLEGE COLUMN
        headers = ['ID', 'First Name', 'Last Name', 'Program', 'College', 'Year', 'Gender']
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        
        # Populate table
        for row, student in enumerate(students):
            # ID column (0)
            table.setItem(row, 0, QTableWidgetItem(student['id']))
            # First Name column (1)
            table.setItem(row, 1, QTableWidgetItem(student['firstname']))
            # Last Name column (2)
            table.setItem(row, 2, QTableWidgetItem(student['lastname']))
            # Program column (3) - SHOW PROGRAM NAME, not code
            table.setItem(row, 3, QTableWidgetItem(student.get('program_name', student['program_code'])))
            # College column (4) - SHOW COLLEGE CODE (automatic from program)
            table.setItem(row, 4, QTableWidgetItem(student.get('college_code', 'N/A')))
            # Year column (5)
            table.setItem(row, 5, QTableWidgetItem(student['year']))
            # Gender column (6)
            table.setItem(row, 6, QTableWidgetItem(student['gender']))
        
        # Resize columns to content
        table.resizeColumnsToContents()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())