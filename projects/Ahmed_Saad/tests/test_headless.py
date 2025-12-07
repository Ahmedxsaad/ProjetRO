import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from src.ui.main_window import MainWindow

def main():
    # Force offscreen
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    
    print("Application started successfully in headless mode.")
    
    # Close after 3 seconds
    QTimer.singleShot(3000, app.quit)
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
