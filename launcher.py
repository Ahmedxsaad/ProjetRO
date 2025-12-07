import sys
import os
import subprocess
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QPushButton, QLabel, QMessageBox, QScrollArea)
from PySide6.QtCore import Qt

class ProjectLauncher(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RO Project Launcher")
        self.resize(500, 600)
        
        # Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Header
        header = QLabel("RO Projects Integration")
        header.setStyleSheet("font-size: 20px; font-weight: bold; margin: 20px;")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Scroll Area for projects
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(15)
        
        # Define Projects
        self.projects = [
            {
                "name": "Ahmed Saad",
                "path": "projects/Ahmed_Saad/main.py",
                "cwd": "projects/Ahmed_Saad",
                "description": "Student Assignment Optimization (PLNE)"
            },
            {
                "name": "Ahmed Ben Rejeb",
                "path": "projects/Ahmed-BenRejeb/run_app.py",
                "cwd": "projects/Ahmed-BenRejeb",
                "description": "Optimization Project (RO 16.3)"
            },
            {
                "name": "Seifeddine Koubaa",
                "path": "projects/skeggo/run.py",
                "cwd": "projects/skeggo",
                "description": "Transport Optimization Application"
            },
            {
                "name": "Abdelkader Ammar",
                "path": "projects/Abdelkader-Ammar/Probleme17.py",
                "cwd": "projects/Abdelkader-Ammar",
                "description": "Graph Flow Optimization (Problem 17)"
            },
            {
                "name": "Amine Jebari",
                "path": "projects/Amine-Jebari/main.py",
                "cwd": "projects/Amine-Jebari",
                "description": "Optimization Problem 15"
            }
        ]
        
        for proj in self.projects:
            btn_widget = QWidget()
            btn_layout = QVBoxLayout(btn_widget)
            
            btn = QPushButton(proj["name"])
            btn.setStyleSheet("font-size: 14px; padding: 10px; font-weight: bold;")
            btn.clicked.connect(lambda checked, p=proj: self.launch_project(p))
            
            desc = QLabel(proj["description"])
            desc.setStyleSheet("color: gray; font-style: italic;")
            desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            btn_layout.addWidget(btn)
            btn_layout.addWidget(desc)
            scroll_layout.addWidget(btn_widget)
            
        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        
        # Footer
        footer = QLabel("Click a button to launch the corresponding project.")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(footer)

    def launch_project(self, project_info):
        try:
            # Resolve absolute paths
            base_dir = os.path.dirname(os.path.abspath(__file__))
            script_path = os.path.join(base_dir, project_info["path"])
            cwd_path = os.path.join(base_dir, project_info["cwd"])
            
            if not os.path.exists(script_path):
                QMessageBox.critical(self, "Error", f"Script not found:\n{script_path}")
                return

            # Launch as subprocess
            # We use sys.executable to ensure we use the same python interpreter (venv)
            subprocess.Popen([sys.executable, script_path], cwd=cwd_path)
            
        except Exception as e:
            QMessageBox.critical(self, "Launch Error", str(e))

def main():
    app = QApplication(sys.argv)
    window = ProjectLauncher()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
