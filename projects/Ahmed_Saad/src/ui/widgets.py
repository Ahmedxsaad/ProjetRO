from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QPushButton, QHeaderView, QSpinBox, 
                             QLineEdit, QLabel, QComboBox, QMessageBox)
from PySide6.QtCore import Qt
from ..model.data_models import Student, Project

class StudentTable(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        # Controls
        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("Add Student")
        self.btn_remove = QPushButton("Remove Selected")
        self.btn_add.clicked.connect(self.add_row)
        self.btn_remove.clicked.connect(self.remove_row)
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_remove)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Preferences (ProjID:Score, ...)"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)

    def add_row(self):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
        self.table.setItem(row, 1, QTableWidgetItem(f"Student {row + 1}"))
        self.table.setItem(row, 2, QTableWidgetItem(""))

    def remove_row(self):
        current_row = self.table.currentRow()
        if current_row >= 0:
            self.table.removeRow(current_row)

    def get_data(self):
        students = []
        for row in range(self.table.rowCount()):
            try:
                s_id = int(self.table.item(row, 0).text())
                name = self.table.item(row, 1).text()
                pref_str = self.table.item(row, 2).text()
                
                prefs = {}
                if pref_str:
                    for part in pref_str.split(','):
                        if ':' in part:
                            pid, score = part.split(':')
                            prefs[int(pid.strip())] = int(score.strip())
                
                students.append(Student(s_id, name, prefs))
            except ValueError:
                continue # Skip invalid rows
        return students

class ProjectTable(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        # Controls
        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("Add Project")
        self.btn_remove = QPushButton("Remove Selected")
        self.btn_add.clicked.connect(self.add_row)
        self.btn_remove.clicked.connect(self.remove_row)
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_remove)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Min Cap", "Max Cap"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)

    def add_row(self):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(str(100 + row + 1)))
        self.table.setItem(row, 1, QTableWidgetItem(f"Project {chr(65+row)}"))
        self.table.setItem(row, 2, QTableWidgetItem("1"))
        self.table.setItem(row, 3, QTableWidgetItem("5"))

    def remove_row(self):
        current_row = self.table.currentRow()
        if current_row >= 0:
            self.table.removeRow(current_row)

    def get_data(self):
        projects = []
        for row in range(self.table.rowCount()):
            try:
                p_id = int(self.table.item(row, 0).text())
                name = self.table.item(row, 1).text()
                min_c = int(self.table.item(row, 2).text())
                max_c = int(self.table.item(row, 3).text())
                projects.append(Project(p_id, name, min_c, max_c))
            except ValueError:
                continue
        return projects

class IncompatibilityWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        # Controls
        input_layout = QHBoxLayout()
        self.spin_s1 = QSpinBox()
        self.spin_s1.setPrefix("Student ID: ")
        self.spin_s1.setRange(0, 9999)
        
        self.spin_s2 = QSpinBox()
        self.spin_s2.setPrefix("Incompatible with ID: ")
        self.spin_s2.setRange(0, 9999)
        
        self.btn_add = QPushButton("Add Constraint")
        self.btn_add.clicked.connect(self.add_constraint)
        
        input_layout.addWidget(self.spin_s1)
        input_layout.addWidget(self.spin_s2)
        input_layout.addWidget(self.btn_add)
        layout.addLayout(input_layout)

        # List
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Student 1", "Student 2"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)
        
        self.btn_remove = QPushButton("Remove Selected Constraint")
        self.btn_remove.clicked.connect(self.remove_row)
        layout.addWidget(self.btn_remove)

    def add_constraint(self):
        s1 = self.spin_s1.value()
        s2 = self.spin_s2.value()
        if s1 == s2:
            return
            
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(str(s1)))
        self.table.setItem(row, 1, QTableWidgetItem(str(s2)))

    def remove_row(self):
        current_row = self.table.currentRow()
        if current_row >= 0:
            self.table.removeRow(current_row)

    def apply_constraints(self, students):
        # Reset incompatibilities
        for s in students:
            s.incompatible_with = []
            
        for row in range(self.table.rowCount()):
            try:
                id1 = int(self.table.item(row, 0).text())
                id2 = int(self.table.item(row, 1).text())
                
                s1 = next((s for s in students if s.id == id1), None)
                s2 = next((s for s in students if s.id == id2), None)
                
                if s1: s1.incompatible_with.append(id2)
                if s2: s2.incompatible_with.append(id1)
            except ValueError:
                continue
