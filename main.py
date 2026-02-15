# mainqt.py - With Edit and Delete Functionality
from PyQt6 import uic
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTableWidgetItem, 
                             QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QComboBox, QPushButton, QMessageBox,
                             QRadioButton, QButtonGroup, QCompleter, QWidget)
from PyQt6.QtCore import Qt
import sys
from database_manager import DatabaseManager
from models import StudentValidator, CollegeValidator


class AddStudentDialog(QDialog):
    """Dialog for adding/editing a student with program names dropdown"""
    
    def __init__(self, db_manager, parent=None, student_data=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.student_data = student_data  # For editing existing student
        self.is_edit_mode = student_data is not None
        
        self.setWindowTitle("Edit Student" if self.is_edit_mode else "Add New Student")
        self.setModal(True)
        self.setMinimumWidth(500)
        
        # Get programs for dropdown
        self.program_display_list = self.db_manager.get_program_display_list()
        
        # Setup UI
        self.setup_ui()
        
        # Pre-fill data if editing
        if self.is_edit_mode:
            self.populate_form()
        
        # Set focus to first input
        self.id_input.setFocus()
    
    def setup_ui(self):
        """Create and arrange all UI elements"""
        layout = QVBoxLayout()
        
        # Form fields
        self.create_id_field(layout)
        self.create_firstname_field(layout)
        self.create_lastname_field(layout)
        self.create_program_field(layout)
        self.create_year_field(layout)
        self.create_gender_field(layout)
        
        layout.addSpacing(20)
        self.create_buttons(layout)
        
        self.setLayout(layout)
    
    def create_id_field(self, layout):
        """Create student ID input field"""
        id_layout = QHBoxLayout()
        id_layout.addWidget(QLabel("Student ID (YYYY-NNNN):*"))
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("2024-0001")
        
        # Disable ID field when editing
        if self.is_edit_mode:
            self.id_input.setReadOnly(True)
            self.id_input.setStyleSheet("background-color: #f0f0f0;")
        
        id_layout.addWidget(self.id_input)
        layout.addLayout(id_layout)
    
    def create_firstname_field(self, layout):
        """Create first name input field"""
        firstname_layout = QHBoxLayout()
        firstname_layout.addWidget(QLabel("First Name:*"))
        self.firstname_input = QLineEdit()
        self.firstname_input.setPlaceholderText("John")
        firstname_layout.addWidget(self.firstname_input)
        layout.addLayout(firstname_layout)
    
    def create_lastname_field(self, layout):
        """Create last name input field"""
        lastname_layout = QHBoxLayout()
        lastname_layout.addWidget(QLabel("Last Name:*"))
        self.lastname_input = QLineEdit()
        self.lastname_input.setPlaceholderText("Smith")
        lastname_layout.addWidget(self.lastname_input)
        layout.addLayout(lastname_layout)
    
    def create_program_field(self, layout):
        """Create program combo box with auto-complete"""
        program_layout = QHBoxLayout()
        program_layout.addWidget(QLabel("Program Name:*"))
        
        self.program_combo = QComboBox()
        self.program_combo.setEditable(True)
        self.program_combo.setMinimumWidth(350)
        
        # Add program names to dropdown
        display_texts = [item['display'] for item in self.program_display_list]
        self.program_combo.addItems(display_texts)
        
        # Set up auto-complete
        completer = QCompleter(display_texts)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.program_combo.setCompleter(completer)
        
        # Store program data for lookup
        self.program_data = {item['display']: item for item in self.program_display_list}
        
        program_layout.addWidget(self.program_combo)
        layout.addLayout(program_layout)
    
    def create_year_field(self, layout):
        """Create year level combo box"""
        year_layout = QHBoxLayout()
        year_layout.addWidget(QLabel("Year Level:*"))
        self.year_combo = QComboBox()
        self.year_combo.addItems(['1', '2', '3', '4', '5'])
        year_layout.addWidget(self.year_combo)
        layout.addLayout(year_layout)
    
    def create_gender_field(self, layout):
        """Create gender radio buttons"""
        gender_layout = QHBoxLayout()
        gender_layout.addWidget(QLabel("Gender:*"))
        
        self.gender_group = QButtonGroup(self)
        self.male_radio = QRadioButton("Male")
        self.female_radio = QRadioButton("Female")
        
        self.gender_group.addButton(self.male_radio)
        self.gender_group.addButton(self.female_radio)
        self.male_radio.setChecked(True)
        
        gender_layout.addWidget(self.male_radio)
        gender_layout.addWidget(self.female_radio)
        layout.addLayout(gender_layout)
    
    def create_buttons(self, layout):
        """Create dialog buttons"""
        button_layout = QHBoxLayout()
        
        save_text = "Update Student" if self.is_edit_mode else "Save Student"
        self.save_button = QPushButton(save_text)
        self.save_button.clicked.connect(self.save_student)
        self.save_button.setDefault(True)
        button_layout.addWidget(self.save_button)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
    
    def populate_form(self):
        """Pre-fill form with existing student data"""
        if not self.student_data:
            return
        
        self.id_input.setText(self.student_data['id'])
        self.firstname_input.setText(self.student_data['firstname'])
        self.lastname_input.setText(self.student_data['lastname'])
        
        # Set program - find matching display text
        program_name = self.student_data.get('program_name', '')
        for i in range(self.program_combo.count()):
            if program_name in self.program_combo.itemText(i):
                self.program_combo.setCurrentIndex(i)
                break
        
        # Set year
        year_index = self.year_combo.findText(self.student_data['year'])
        if year_index >= 0:
            self.year_combo.setCurrentIndex(year_index)
        
        # Set gender
        if self.student_data['gender'] == 'Male':
            self.male_radio.setChecked(True)
        else:
            self.female_radio.setChecked(True)
    
    def get_selected_program_code(self):
        """Extract program code from selected display text"""
        selected_text = self.program_combo.currentText().strip()
        
        if selected_text in self.program_data:
            return self.program_data[selected_text]['code']
        
        # Try partial match
        for display, data in self.program_data.items():
            if selected_text.lower() in display.lower():
                return data['code']
        
        return None
    
    def validate_student_data(self, student_data):
        """Validate all student data fields"""
        # Validate Student ID
        valid, message = StudentValidator.validate_student_id(student_data['id'])
        if not valid:
            QMessageBox.warning(self, "Validation Error", message)
            self.id_input.setFocus()
            return False
        
        # Validate First Name
        valid, message = StudentValidator.validate_name(student_data['firstname'], "First Name")
        if not valid:
            QMessageBox.warning(self, "Validation Error", message)
            self.firstname_input.setFocus()
            return False
        
        # Validate Last Name
        valid, message = StudentValidator.validate_name(student_data['lastname'], "Last Name")
        if not valid:
            QMessageBox.warning(self, "Validation Error", message)
            self.lastname_input.setFocus()
            return False
        
        # Validate Program Selection
        if not student_data['program_code']:
            QMessageBox.warning(self, "Validation Error", 
                              "Please select a valid program from the list")
            self.program_combo.setFocus()
            return False
        
        if not self.db_manager.program_exists(student_data['program_code']):
            QMessageBox.warning(self, "Validation Error", 
                              f"Program '{self.program_combo.currentText()}' does not exist.\n"
                              "Please select a program from the list.")
            self.program_combo.setFocus()
            return False
        
        # Validate Year
        valid, message = StudentValidator.validate_year(student_data['year'])
        if not valid:
            QMessageBox.warning(self, "Validation Error", message)
            return False
        
        return True
    
    def get_student_data(self):
        """Collect data from form inputs"""
        selected_program_code = self.get_selected_program_code()
        
        return {
            'id': self.id_input.text().strip(),
            'firstname': self.firstname_input.text().strip(),
            'lastname': self.lastname_input.text().strip(),
            'program_code': selected_program_code,
            'year': self.year_combo.currentText(),
            'gender': 'Male' if self.male_radio.isChecked() else 'Female'
        }
    
    def save_student(self):
        """Validate and save the student"""
        student_data = self.get_student_data()
        
        if not self.validate_student_data(student_data):
            return
        
        # Confirmation dialog
        program_display = self.program_combo.currentText()
        action = "update" if self.is_edit_mode else "add"
        confirm_msg = (
            f"Are you sure you want to {action} this student?\n\n"
            f"Student ID: {student_data['id']}\n"
            f"Name: {student_data['lastname']}, {student_data['firstname']}\n"
            f"Program: {program_display}\n"
            f"Year: {student_data['year']}\n"
            f"Gender: {student_data['gender']}"
        )
        
        reply = QMessageBox.question(
            self, f"Confirm {action.title()}", confirm_msg,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.is_edit_mode:
                success, message = self.db_manager.update_student(student_data)
            else:
                success, message = self.db_manager.add_student(student_data)
            
            if success:
                QMessageBox.information(self, "Success", message)
                self.accept()
            else:
                QMessageBox.critical(self, "Error", message)


class AddCollegeDialog(QDialog):
    """Dialog for adding/editing colleges"""
    
    def __init__(self, db_manager, parent=None, college_data=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.college_data = college_data  # For editing existing colleges
        self.is_edit_mode = college_data is not None
        
        self.setWindowTitle("Edit College" if self.is_edit_mode else "Add New College")
        self.setModal(True)
        self.setMinimumWidth(400)
        
        # Setup UI
        self.setup_ui()
        
        # Pre-fill data if editing
        if self.is_edit_mode:
            self.populate_form()
        
        # Set focus to first input
        self.collegename_input.setFocus()
    
    def setup_ui(self):
        """Create and arrange all UI elements"""
        layout = QVBoxLayout()
        
        # Form fields
        self.create_collegename_field(layout)
        self.create_collegecode_field(layout)
        
        layout.addSpacing(20)
        self.create_buttons(layout)
        
        self.setLayout(layout)
    
    def create_collegename_field(self, layout):
        """Create college name input field"""
        collegename_layout = QHBoxLayout()
        collegename_layout.addWidget(QLabel("College name:*"))
        self.collegename_input = QLineEdit()
        self.collegename_input.setPlaceholderText("College of Computer Studies")
        collegename_layout.addWidget(self.collegename_input)
        layout.addLayout(collegename_layout)
        
    def create_collegecode_field(self, layout):
        """Create college code input field"""
        collegecode_layout = QHBoxLayout()
        collegecode_layout.addWidget(QLabel("College Code (2-5 letters):*"))
        self.collegecode_input = QLineEdit()
        self.collegecode_input.setPlaceholderText("CCS")
        collegecode_layout.addWidget(self.collegecode_input)
        layout.addLayout(collegecode_layout)
    
        # Disable college code field when editing
        if self.is_edit_mode:
            self.collegecode_input.setReadOnly(True)
            self.collegecode_input.setStyleSheet("background-color: #f0f0f0;")
    
    def create_buttons(self, layout):
        """Create dialog buttons"""
        button_layout = QHBoxLayout()
        
        save_text = "Update College" if self.is_edit_mode else "Save College"
        self.save_button = QPushButton(save_text)
        self.save_button.clicked.connect(self.save_college)
        self.save_button.setDefault(True)
        button_layout.addWidget(self.save_button)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
    
    def populate_form(self):
        """Pre-fill form with existing college data"""
        if not self.college_data:
            return
        
        self.collegename_input.setText(self.college_data['name'])
        self.collegecode_input.setText(self.college_data['code'])
    
    def validate_college_data(self, college_data):
        """Validate all college data fields"""

        # Validate college name
        valid, message = CollegeValidator.validate_college_name(college_data['name'])
        if not valid:
            QMessageBox.warning(self, "Validation Error", message)
            self.collegename_input.setFocus()
            return False
        
        # Validate college code format
        valid, message = CollegeValidator.validate_college_code(college_data['code'])
        if not valid:
            QMessageBox.warning(self, "Validation Error", message)
            self.collegecode_input.setFocus()
            return False
        
        return True
    
    def get_college_data(self):
        """Collect data from form inputs"""
        college_data = {
            'code': self.collegecode_input.text().strip().upper(),
            'name': self.collegename_input.text().strip()
        }
        
        # Add ID if editing existing college
        if self.is_edit_mode and self.college_data:
            college_data['id'] = self.college_data.get('id')
        
        return college_data
    
    def save_college(self):
        """Validate and save the college"""
        college_data = self.get_college_data()
        
        if not self.validate_college_data(college_data):
            return
        
        # Confirmation dialog
        action = "update" if self.is_edit_mode else "add"
        confirm_msg = (
            f"Are you sure you want to {action} this college?\n\n"
            f"College Code: {college_data['code']}\n"
            f"College Name: {college_data['name']}"
        )
        
        reply = QMessageBox.question(
            self, f"Confirm {action.title()}", confirm_msg,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.is_edit_mode:
                success, message = self.db_manager.update_college(college_data)
            else:
                success, message = self.db_manager.add_college(college_data)
            
            if success:
                QMessageBox.information(self, "Success", message)
                self.accept()
            else:
                QMessageBox.critical(self, "Error", message)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        uic.loadUi('main_window.ui', self)
        self.db_manager = DatabaseManager()
        
        self.connect_buttons()
        self.load_students_table()
        self.load_colleges_table()
    
    def connect_buttons(self):
        """Connect UI buttons to their functions"""
        self.studentsButton.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0))
        self.programsButton.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(1))
        self.collegesButton.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(2))
        self.addStudentButton.clicked.connect(self.open_add_student_dialog)
        self.addCollegeButton.clicked.connect(self.open_add_college_dialog)

        # Connect sort dropdown
        self.sortComboBox_2.currentTextChanged.connect(self.sort_students_by_dropdown)
    
    def sort_students_by_dropdown(self, sort_by):
        """Sort students table based on dropdown selection"""
        table = self.dataTableStudents
    
        # Map dropdown options to column indices
        sort_mapping = {
            'Program': 3,   # Program column
            'Name': 2,      # Last Name column  
            'ID': 0,        # ID column
            'College': 4,    # College column
            'Year' : 5      
        }
    
        column = sort_mapping.get(sort_by)
        if column is not None:
            table.sortItems(column, Qt.SortOrder.AscendingOrder)
    
    def open_add_student_dialog(self):
        """Open the Add Student dialog"""
        dialog = AddStudentDialog(self.db_manager, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_students_table()
    
    def open_edit_student_dialog(self, row):
        """Open the Edit Student dialog with pre-filled data"""
        # Get student data from the table row
        student_data = {
            'id': self.dataTableStudents.item(row, 0).text(),
            'firstname': self.dataTableStudents.item(row, 1).text(),
            'lastname': self.dataTableStudents.item(row, 2).text(),
            'program_name': self.dataTableStudents.item(row, 3).text(),
            'year': self.dataTableStudents.item(row, 5).text(),
            'gender': self.dataTableStudents.item(row, 6).text()
        }
        
        dialog = AddStudentDialog(self.db_manager, self, student_data)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_students_table()
    
    def delete_student(self, row):
        """Delete student after confirmation"""
        # Get student info
        student_id = self.dataTableStudents.item(row, 0).text()
        firstname = self.dataTableStudents.item(row, 1).text()
        lastname = self.dataTableStudents.item(row, 2).text()
        student_name = f"{firstname} {lastname}"
        
        # Confirmation dialog
        reply = QMessageBox.question(
            self,
            'Delete Student',
            f'Are you sure you want to delete student:\n\n'
            f'{student_name} (ID: {student_id})?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Delete from database
            success, message = self.db_manager.delete_student(student_id)
            
            if success:
                # Reload table
                self.load_students_table()
                QMessageBox.information(self, "Success", message)
            else:
                QMessageBox.critical(self, "Error", message)
    
    def add_action_buttons(self, row):
        """Add Edit and Delete buttons to a table row"""
        # Create a widget to hold the buttons
        button_widget = QWidget()
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(4, 2, 4, 2)
        button_layout.setSpacing(4)
        
        # Edit button
        edit_btn = QPushButton("✏️ Edit")
        edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        edit_btn.clicked.connect(lambda checked, r=row: self.open_edit_student_dialog(r))
        
        # Delete button
        delete_btn = QPushButton("🗑️ Delete")
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        delete_btn.clicked.connect(lambda checked, r=row: self.delete_student(r))
        
        # Add buttons to layout
        button_layout.addWidget(edit_btn)
        button_layout.addWidget(delete_btn)
        button_widget.setLayout(button_layout)
        
        # Add to table (column 7 is the Actions column)
        self.dataTableStudents.setCellWidget(row, 7, button_widget)
    
    def load_students_table(self):
        """Load students from database into the table"""
        table = self.dataTableStudents
        table.setSortingEnabled(False)
        table.setRowCount(0)
        
        students = self.db_manager.get_students_with_details()
        table.setRowCount(len(students))
        
        headers = ['ID', 'First Name', 'Last Name', 'Program', 'College', 'Year', 'Gender', 'Actions']
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        
        for row, student in enumerate(students):
            table.setItem(row, 0, QTableWidgetItem(student['id']))
            table.setItem(row, 1, QTableWidgetItem(student['firstname']))
            table.setItem(row, 2, QTableWidgetItem(student['lastname']))
            table.setItem(row, 3, QTableWidgetItem(student.get('program_name', student['program_code'])))
            table.setItem(row, 4, QTableWidgetItem(student.get('college_code', 'N/A')))
            table.setItem(row, 5, QTableWidgetItem(student['year']))
            table.setItem(row, 6, QTableWidgetItem(student['gender']))
            
            # Add action buttons to each row
            self.add_action_buttons(row)
        
        table.resizeColumnsToContents()

        """Enables sort function"""
        table.setSortingEnabled(True)

    def open_add_college_dialog(self):
        """Open the Add College dialog"""
        dialog = AddCollegeDialog(self.db_manager, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_colleges_table()

    def load_colleges_table(self):
        """Load colleges from database into the table"""
        table = self.dataTableColleges
        table.setSortingEnabled(False)
        table.setRowCount(0)
        
        colleges = self.db_manager.get_all_colleges()
        table.setRowCount(len(colleges))
    
        for row, college in enumerate(colleges):
            table.setItem(row, 0, QTableWidgetItem(college['name']))
            table.setItem(row, 1, QTableWidgetItem(college['code']))
        
            # Add action buttons to the Actions column (column index 2)
            self.add_action_buttons_college(row, college)
    
        # Adjust column widths
        table.resizeColumnsToContents()
        table.horizontalHeader().setStretchLastSection(False)
    
        # Make Actions column fixed width
        table.setColumnWidth(2, 150)
    
        # Enable sorting
        table.setSortingEnabled(True)

    def add_action_buttons_college(self, row, college):
        """Add Edit and Delete buttons for each college row"""

        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        button_layout.setContentsMargins(4, 2, 4, 2)
        button_layout.setSpacing(4)
        
        # Edit button
        edit_btn = QPushButton("✏️ Edit")
        edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        edit_btn.clicked.connect(lambda checked, c=college: self.edit_college(c))
        
        # Delete button
        delete_btn = QPushButton("🗑️ Delete")
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        delete_btn.clicked.connect(lambda checked, c=college: self.delete_college(c))
        
        button_layout.addWidget(edit_btn)
        button_layout.addWidget(delete_btn)
        
        self.dataTableColleges.setCellWidget(row, 2, button_widget)

    def edit_college(self, college):
        """Open dialog to edit college"""
        dialog = AddCollegeDialog(self.db_manager, self, college_data=college)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_colleges_table()

    def delete_college(self, college):
        """Delete a college after confirmation"""
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete {college['name']} ({college['code']})?\n\n"
            f"Warning: This may affect associated courses and students!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            success, message = self.db_manager.delete_college(college['code'])
            if success:
                QMessageBox.information(self, "Success", message)
                self.load_colleges_table()
            else:
                QMessageBox.critical(self, "Error", message)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())