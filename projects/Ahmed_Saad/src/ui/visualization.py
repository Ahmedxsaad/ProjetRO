from PySide6.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QLabel, QTabWidget)
from PySide6.QtCore import Qt
import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import networkx as nx

class ResultsView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        self.summary_label = QLabel("No results yet.")
        layout.addWidget(self.summary_label)
        
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Student", "Assigned Project", "Preference Score"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabs.addTab(self.table, "Table")
        
        self.graph_view = GraphView()
        self.tabs.addTab(self.graph_view, "Graph")

    def update_results(self, result, students, projects):
        self.summary_label.setText(f"Status: {result.status} | Objective: {result.objective_value} | Time: {result.solve_time:.4f}s")
        
        # Update Table
        self.table.setRowCount(0)
        for s_id, p_id in result.student_assignments.items():
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            s_name = next((s.name for s in students if s.id == s_id), str(s_id))
            p_name = next((p.name for p in projects if p.id == p_id), str(p_id))
            
            # Find score
            student = next((s for s in students if s.id == s_id), None)
            score = student.preferences.get(p_id, 0) if student else 0
            
            self.table.setItem(row, 0, QTableWidgetItem(s_name))
            self.table.setItem(row, 1, QTableWidgetItem(p_name))
            self.table.setItem(row, 2, QTableWidgetItem(str(score)))
            
        # Update Graph
        self.graph_view.plot(result, students, projects)

class GraphView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        self.figure = Figure()
        self.canvas = FigureCanvasQTAgg(self.figure)
        layout.addWidget(self.canvas)

    def plot(self, result, students, projects):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        G = nx.Graph()
        
        # Add nodes
        left_nodes = [s.id for s in students]
        right_nodes = [p.id for p in projects]
        
        G.add_nodes_from(left_nodes, bipartite=0)
        G.add_nodes_from(right_nodes, bipartite=1)
        
        # Add edges (assignments)
        edges = []
        for s_id, p_id in result.student_assignments.items():
            edges.append((s_id, p_id))
        G.add_edges_from(edges)
        
        # Layout
        pos = nx.bipartite_layout(G, left_nodes)
        
        # Draw
        nx.draw_networkx_nodes(G, pos, nodelist=left_nodes, node_color='skyblue', node_size=500, ax=ax, label='Students')
        nx.draw_networkx_nodes(G, pos, nodelist=right_nodes, node_color='lightgreen', node_size=700, ax=ax, label='Projects')
        nx.draw_networkx_edges(G, pos, ax=ax)
        
        # Labels
        labels = {s.id: s.name for s in students}
        labels.update({p.id: p.name for p in projects})
        nx.draw_networkx_labels(G, pos, labels, font_size=10, ax=ax)
        
        ax.set_title("Assignment Graph")
        ax.axis('off')
        self.canvas.draw()
