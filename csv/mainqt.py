from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Load the .ui file
        uic.loadUi('main_window.ui', self)
        
        # Connect buttons directly
        self.studentsButton.clicked.connect(lambda: self.rightWidget.setCurrentIndex(0))
        self.collegesButton.clicked.connect(lambda: self.rightWidget.setCurrentIndex(2))
        self.programsButton.clicked.connect(lambda: self.rightWidget.setCurrentIndex(1))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())