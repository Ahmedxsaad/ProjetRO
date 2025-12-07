from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QTabWidget, 
                             QLabel, QPushButton, QHBoxLayout, QStatusBar, QMessageBox,
                             QTableWidgetItem)
from PySide6.QtCore import Qt, QThread, Signal
import sys
import os

# Import backend logic
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from src.model.data_models import Student, Project
from src.model.optimization_model import StudentAssignmentSolver
from src.model.mock_solver import MockSolver

class SolverThread(QThread):
    finished = Signal(object)
    error = Signal(str)

    def __init__(self, solver, students, projects):
        super().__init__()
        self.solver = solver
        self.students = students
        self.projects = projects

    def run(self):
        try:
            result = self.solver.solve(self.students, self.projects)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))

from .widgets import StudentTable, ProjectTable, IncompatibilityWidget
from .visualization import ResultsView

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Project Assignment Optimization")
        self.resize(1200, 800)

        # Central Widget & Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Header
        header = QLabel("Student Project Assignment (PLNE)")
        header.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)

        # Tabs
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Initialize Widgets
        self.student_widget = StudentTable()
        self.project_widget = ProjectTable()
        self.constraint_widget = IncompatibilityWidget()
        self.results_widget = ResultsView()
        self.tab_solver = QWidget()

        self.tabs.addTab(self.student_widget, "1. Students")
        self.tabs.addTab(self.project_widget, "2. Projects")
        self.tabs.addTab(self.constraint_widget, "3. Constraints")
        self.tabs.addTab(self.tab_solver, "4. Solve")
        self.tabs.addTab(self.results_widget, "5. Results")

        # Setup Solver Tab
        self.setup_solver_tab()

        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

        # Pre-populate with some dummy data for demo
        self.populate_demo_data()
    
    def populate_demo_data(self):
        # Add 5 students
        for i in range(5):
            self.student_widget.add_row()
            # Set some prefs
            self.student_widget.table.setItem(i, 2, QTableWidgetItem(f"101:{10-i}, 102:{i+1}"))
            
        # Add 2 projects
        self.project_widget.add_row() # P1
        self.project_widget.add_row() # P2
        # Set caps
        self.project_widget.table.setItem(0, 2, QTableWidgetItem("1"))
        self.project_widget.table.setItem(0, 3, QTableWidgetItem("3"))
        self.project_widget.table.setItem(1, 2, QTableWidgetItem("1"))
        self.project_widget.table.setItem(1, 3, QTableWidgetItem("3"))

    def setup_solver_tab(self):
        layout = QVBoxLayout(self.tab_solver)
        
        info_label = QLabel("Click 'Run Solver' to optimize assignments.")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info_label)

        btn_layout = QHBoxLayout()
        self.btn_solve = QPushButton("Run Gurobi Solver")
        self.btn_solve.clicked.connect(lambda: self.run_solver(use_mock=False))
        
        self.btn_mock = QPushButton("Run Mock Solver (Test)")
        self.btn_mock.clicked.connect(lambda: self.run_solver(use_mock=True))

        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_solve)
        btn_layout.addWidget(self.btn_mock)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        layout.addStretch()

    def run_solver(self, use_mock=False):
        self.status_bar.showMessage("Solving...")
        self.btn_solve.setEnabled(False)
        self.btn_mock.setEnabled(False)

        # Gather data
        self.students = self.student_widget.get_data()
        self.projects = self.project_widget.get_data()
        self.constraint_widget.apply_constraints(self.students)

        if not self.students or not self.projects:
            QMessageBox.warning(self, "Warning", "Please add students and projects first.")
            self.btn_solve.setEnabled(True)
            self.btn_mock.setEnabled(True)
            return

        solver = MockSolver() if use_mock else StudentAssignmentSolver()
        
        self.thread = SolverThread(solver, self.students, self.projects)
        self.thread.finished.connect(self.on_solver_finished)
        self.thread.error.connect(self.on_solver_error)
        self.thread.start()

    def on_solver_finished(self, result):
        self.status_bar.showMessage(f"Solved: {result.status}")
        self.btn_solve.setEnabled(True)
        self.btn_mock.setEnabled(True)
        
        self.results_widget.update_results(result, self.students, self.projects)
        self.tabs.setCurrentWidget(self.results_widget)

    def on_solver_error(self, error_msg):
        self.status_bar.showMessage("Error")
        self.btn_solve.setEnabled(True)
        self.btn_mock.setEnabled(True)
        QMessageBox.critical(self, "Solver Error", error_msg)
