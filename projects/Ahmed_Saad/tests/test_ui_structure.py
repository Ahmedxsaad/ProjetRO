import unittest
import sys
import os
from PySide6.QtWidgets import QApplication

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

# We need a QApplication instance to create widgets
app = QApplication(sys.argv)

from ui.main_window import MainWindow

class TestUI(unittest.TestCase):
    def test_mainwindow_instantiation(self):
        """Test that MainWindow can be instantiated without crashing"""
        try:
            window = MainWindow()
            self.assertIsNotNone(window)
            # Check if widgets are present
            self.assertIsNotNone(window.student_widget)
            self.assertIsNotNone(window.project_widget)
            self.assertIsNotNone(window.results_widget)
        except Exception as e:
            self.fail(f"MainWindow instantiation failed: {e}")

if __name__ == '__main__':
    unittest.main()
