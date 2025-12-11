import sys
import os
import subprocess
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QPushButton, QLabel, QMessageBox, QScrollArea, QFrame)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIcon

class ProjectLauncher(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lanceur de Projets RO")
        self.resize(600, 750)
        
        # Modern Dark Theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e2e;
            }
            QLabel {
                color: #cdd6f4;
                font-family: 'Segoe UI', sans-serif;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QWidget#scrollContent {
                background-color: transparent;
            }
            QFrame.project-card {
                background-color: #313244;
                border-radius: 12px;
                border: 1px solid #45475a;
            }
            QFrame.project-card:hover {
                background-color: #45475a;
                border: 1px solid #89b4fa;
            }
            QPushButton {
                background-color: #89b4fa;
                color: #1e1e2e;
                border: none;
                border-radius: 6px;
                padding: 8px 20px;
                font-weight: bold;
                font-family: 'Segoe UI', sans-serif;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #b4befe;
            }
            QLabel#header {
                font-size: 28px;
                font-weight: bold;
                color: #89b4fa;
                margin-bottom: 20px;
                margin-top: 10px;
            }
            QLabel#student-name {
                font-size: 20px;
                font-weight: bold;
                color: #f38ba8;
            }
            QLabel#project-title {
                font-size: 16px;
                font-weight: bold;
                color: #fab387;
                margin-top: 4px;
            }
            QLabel#project-desc {
                font-size: 13px;
                color: #a6adc8;
                font-style: italic;
                margin-top: 4px;
                margin-bottom: 8px;
            }
            QLabel#footer {
                color: #6c7086; 
                margin-top: 10px;
                font-size: 12px;
            }
        """)
        
        # Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Header
        header = QLabel("Intégration des Projets RO")
        header.setObjectName("header")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Scroll Area for projects
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_content.setObjectName("scrollContent")
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(20)
        scroll_layout.setContentsMargins(0, 10, 0, 10)
        
        # Define Projects
        self.projects = [
            {
                "name": "Ahmed Saad",
                "title": "13. Couplage Maximum PLNE (B)",
                "path": "projects/Ahmed_Saad/main.py",
                "cwd": "projects/Ahmed_Saad",
                "description": "Trouver le plus grand ensemble d'arêtes qui ne partagent aucun nœud (par exemple, marier des hommes et des femmes)."
            },
            {
                "name": "Seif Koubaa",
                "title": "14. Flux à Coût Minimum PL",
                "path": "projects/skeggo/run.py",
                "cwd": "projects/skeggo",
                "description": "Trouver le flux admissible d'une source à un puits dans un réseau avec des coûts associés à chaque arc, en minimisant le coût total."
            },
            {
                "name": "Amine Jebari",
                "title": "15. Poids Minimum de Sommets/Arêtes PLNE",
                "path": "projects/Amine-Jebari/main.py",
                "cwd": "projects/Amine-Jebari",
                "description": "Sélectionner un sous-ensemble de sommets (ou d'arêtes) avec le poids minimal pour satisfaire une certaine propriété (couverture, connectivité)."
            },
            {
                "name": "Ahmed Ben Rejeb",
                "title": "16. Mélange (Blending Problem) PL",
                "path": "projects/Ahmed-BenRejeb/run_app.py",
                "cwd": "projects/Ahmed-BenRejeb",
                "description": "Déterminer les proportions de différentes matières premières à mélanger pour obtenir un produit final satisfaisant des contraintes de qualité au coût minimal."
            },
            {
                "name": "Abdelkader Ammar",
                "title": "17. Flot Maximum PL",
                "path": "projects/Abdelkader-Ammar/Probleme17.py",
                "cwd": "projects/Abdelkader-Ammar",
                "description": "Déterminer le débit maximum possible d'une source à un puits dans un réseau avec des capacités limitées sur les arêtes."
            }
        ]
        
        for proj in self.projects:
            card = QFrame()
            card.setProperty("class", "project-card")
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(20, 20, 20, 20)
            
            # Info Section
            name_label = QLabel(proj["name"])
            name_label.setObjectName("student-name")
            
            title_label = QLabel(proj["title"])
            title_label.setObjectName("project-title")
            title_label.setWordWrap(True)
            
            desc_label = QLabel(proj["description"])
            desc_label.setObjectName("project-desc")
            desc_label.setWordWrap(True)
            
            # Button Section
            launch_btn = QPushButton("Lancer le Projet")
            launch_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            launch_btn.clicked.connect(lambda checked, p=proj: self.launch_project(p))
            
            card_layout.addWidget(name_label)
            card_layout.addWidget(title_label)
            card_layout.addWidget(desc_label)
            card_layout.addSpacing(10)
            card_layout.addWidget(launch_btn, 0, Qt.AlignmentFlag.AlignRight)
            
            scroll_layout.addWidget(card)
            
        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        
        # Footer
        footer = QLabel("Cliquez sur 'Lancer le Projet' pour exécuter l'application correspondante.")
        footer.setObjectName("footer")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(footer)

    def launch_project(self, project_info):
        try:
            # Resolve absolute paths
            base_dir = os.path.dirname(os.path.abspath(__file__))
            script_path = os.path.join(base_dir, project_info["path"])
            cwd_path = os.path.join(base_dir, project_info["cwd"])
            
            if not os.path.exists(script_path):
                QMessageBox.critical(self, "Erreur", f"Script introuvable :\n{script_path}")
                return

            # Launch as subprocess
            subprocess.Popen([sys.executable, script_path], cwd=cwd_path)
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur de Lancement", str(e))

def main():
    app = QApplication(sys.argv)
    window = ProjectLauncher()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
