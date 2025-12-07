import sys
import os

# Ensure correct path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QTableWidget, QTableWidgetItem, QTabWidget, 
                             QComboBox, QMessageBox, QHeaderView)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import networkx as nx

# Import optimization model
from TransportApp.model.optimization import MinCostFlowModel

class OptimizationWorker(QThread):
    finished = pyqtSignal(object)
    error = pyqtSignal(str)

    def __init__(self, model, data):
        super().__init__()
        self.model = model
        self.data = data

    def run(self):
        try:
            self.model.set_data(
                self.data['hubs'],
                self.data['modes'],
                self.data['arcs'],
                self.data['demands'],
                self.data['capacities'],
                self.data['costs'],
                self.data['hub_capacities']
            )
            self.model.build_model()
            result = self.model.solve()
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Multi-Modal Passenger Transport Optimizer")
        self.resize(1200, 800)
        
        # Data Storage
        self.hubs = []
        self.modes = ['Train', 'Bus', 'Flight']
        self.arcs = []
        self.demands = {} 
        self.capacities = {} 
        self.costs = {} 
        self.hub_capacities = {} 

        # Main Layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Tabs
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Tab 1: Data Entry (Hubs & Demands)
        self.tab_hubs = QWidget()
        self.setup_hubs_tab()
        self.tabs.addTab(self.tab_hubs, "1. Hubs & Demand")
        
        # Tab 2: Arcs & Costs
        self.tab_arcs = QWidget()
        self.setup_arcs_tab()
        self.tabs.addTab(self.tab_arcs, "2. Routes (Arcs)")
        
        # Tab 3: Results
        self.tab_results = QWidget()
        self.setup_results_tab()
        self.tabs.addTab(self.tab_results, "3. Optimization Results")

        # Initialize Model
        self.model = MinCostFlowModel()

    def setup_hubs_tab(self):
        layout = QVBoxLayout(self.tab_hubs)
        
        # Input Form
        form_layout = QHBoxLayout()
        self.hub_name_input = QLineEdit()
        self.hub_name_input.setPlaceholderText("Hub Name (e.g., Paris)")
        
        self.demand_input = QLineEdit()
        self.demand_input.setPlaceholderText("Net Demand (+Supply/-Demand)")
        
        self.hub_cap_input = QLineEdit()
        self.hub_cap_input.setPlaceholderText("Max Transit Capacity")
        
        add_btn = QPushButton("Add Hub")
        add_btn.clicked.connect(self.add_hub)
        
        form_layout.addWidget(QLabel("Name:"))
        form_layout.addWidget(self.hub_name_input)
        form_layout.addWidget(QLabel("Demand:"))
        form_layout.addWidget(self.demand_input)
        form_layout.addWidget(QLabel("Capacity:"))
        form_layout.addWidget(self.hub_cap_input)
        form_layout.addWidget(add_btn)
        
        layout.addLayout(form_layout)
        
        # Table
        self.hubs_table = QTableWidget()
        self.hubs_table.setColumnCount(3)
        self.hubs_table.setHorizontalHeaderLabels(["Hub Name", "Net Demand", "Max Capacity"])
        self.hubs_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.hubs_table)

    def add_hub(self):
        name = self.hub_name_input.text().strip()
        try:
            demand = float(self.demand_input.text().strip())
            cap_text = self.hub_cap_input.text().strip()
            cap = float(cap_text) if cap_text else 10000.0
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Demand and Capacity must be numbers.")
            return

        if not name:
            return

        if name in self.hubs:
            QMessageBox.warning(self, "Error", "Hub already exists.")
            return
            
        self.hubs.append(name)
        self.demands[name] = demand
        self.hub_capacities[name] = cap
        
        row = self.hubs_table.rowCount()
        self.hubs_table.insertRow(row)
        self.hubs_table.setItem(row, 0, QTableWidgetItem(name))
        self.hubs_table.setItem(row, 1, QTableWidgetItem(str(demand)))
        self.hubs_table.setItem(row, 2, QTableWidgetItem(str(cap)))
        
        # Update Combo boxes in other tabs
        self.update_combos()
        
        self.hub_name_input.clear()
        self.demand_input.clear()
        self.hub_cap_input.clear()

    def setup_arcs_tab(self):
        layout = QVBoxLayout(self.tab_arcs)
        
        # Form
        form_layout = QHBoxLayout()
        
        self.origin_combo = QComboBox()
        self.dest_combo = QComboBox()
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(self.modes)
        
        self.cost_input = QLineEdit()
        self.cost_input.setPlaceholderText("Cost per passenger")
        
        self.link_cap_input = QLineEdit()
        self.link_cap_input.setPlaceholderText("Max Passengers")
        
        add_btn = QPushButton("Add Route")
        add_btn.clicked.connect(self.add_arc)
        
        form_layout.addWidget(QLabel("From:"))
        form_layout.addWidget(self.origin_combo)
        form_layout.addWidget(QLabel("To:"))
        form_layout.addWidget(self.dest_combo)
        form_layout.addWidget(QLabel("Mode:"))
        form_layout.addWidget(self.mode_combo)
        form_layout.addWidget(QLabel("Cost:"))
        form_layout.addWidget(self.cost_input)
        form_layout.addWidget(QLabel("Link Cap:"))
        form_layout.addWidget(self.link_cap_input)
        form_layout.addWidget(add_btn)
        
        layout.addLayout(form_layout)
        
        # Table
        self.arcs_table = QTableWidget()
        self.arcs_table.setColumnCount(5)
        self.arcs_table.setHorizontalHeaderLabels(["Origin", "Destination", "Mode", "Cost", "Capacity"])
        self.arcs_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.arcs_table)

    def update_combos(self):
        self.origin_combo.clear()
        self.dest_combo.clear()
        self.origin_combo.addItems(self.hubs)
        self.dest_combo.addItems(self.hubs)

    def add_arc(self):
        u = self.origin_combo.currentText()
        v = self.dest_combo.currentText()
        mode = self.mode_combo.currentText()
        
        if not u or not v:
            return
        if u == v:
            QMessageBox.warning(self, "Error", "Origin and Destination cannot be the same.")
            return
            
        try:
            cost = float(self.cost_input.text())
            cap = float(self.link_cap_input.text())
        except ValueError:
            QMessageBox.warning(self, "Error", "Cost and Capacity must be numbers.")
            return
            
        # Add to data structures
        if (u, v) not in self.arcs:
            self.arcs.append((u, v))
            
        self.costs[(u, v, mode)] = cost
        self.capacities[(u, v, mode)] = cap
        
        # Update Table
        row = self.arcs_table.rowCount()
        self.arcs_table.insertRow(row)
        self.arcs_table.setItem(row, 0, QTableWidgetItem(u))
        self.arcs_table.setItem(row, 1, QTableWidgetItem(v))
        self.arcs_table.setItem(row, 2, QTableWidgetItem(mode))
        self.arcs_table.setItem(row, 3, QTableWidgetItem(str(cost)))
        self.arcs_table.setItem(row, 4, QTableWidgetItem(str(cap)))

    def setup_results_tab(self):
        layout = QVBoxLayout(self.tab_results)
        
        solve_btn = QPushButton("SOLVE OPTIMIZATION")
        solve_btn.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px; background-color: #4CAF50; color: white;")
        solve_btn.clicked.connect(self.run_optimization)
        layout.addWidget(solve_btn)
        
        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)
        
        # Graph Visualization
        self.figure = plt.figure(figsize=(8, 6))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
        # Text Output
        self.results_text = QLabel("")
        self.results_text.setWordWrap(True)
        layout.addWidget(self.results_text)

    def run_optimization(self):
        self.status_label.setText("Solving... Please wait.")
        
        # Prepare Data
        data = {
            'hubs': self.hubs,
            'modes': self.modes,
            'arcs': self.arcs,
            'demands': self.demands,
            'capacities': self.capacities,
            'costs': self.costs,
            'hub_capacities': self.hub_capacities
        }
        
        self.worker = OptimizationWorker(self.model, data)
        self.worker.finished.connect(self.on_optimization_finished)
        self.worker.error.connect(self.on_optimization_error)
        self.worker.start()

    def on_optimization_finished(self, result):
        self.status_label.setText(f"Status: {result.get('status', 'Unknown')}")
        
        if result['status'] == 'Optimal':
            obj_val = result['objective']
            flows = result['flows']
            
            text = f"<b>Optimal Total Cost: {obj_val}</b><br><br>Flows:<br>"
            for (u, v, k), flow in flows.items():
                text += f"{u} -> {v} ({k}): {flow} passengers<br>"
            self.results_text.setText(text)
            
            self.visualize_solution(flows)
        else:
            self.results_text.setText(f"No optimal solution found. Status: {result.get('code', 'Unknown')}")

    def on_optimization_error(self, error_msg):
        self.status_label.setText("Error")
        QMessageBox.critical(self, "Optimization Error", error_msg)

    def visualize_solution(self, flows):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        G = nx.MultiDiGraph()
        
        for node in self.hubs:
            G.add_node(node)
            
        pos = nx.spring_layout(G) 
        
        # Draw Nodes
        nx.draw_networkx_nodes(G, pos, ax=ax, node_size=700, node_color='lightblue')
        nx.draw_networkx_labels(G, pos, ax=ax)
        
        # Draw Edges
        aggregated_flows = {}
        for (u, v, k), flow in flows.items():
            if (u,v) not in aggregated_flows:
                aggregated_flows[(u,v)] = []
            aggregated_flows[(u,v)].append(f"{k}: {flow}")
            
        for (u, v), flow_list in aggregated_flows.items():
            label = "\n".join(flow_list)
            G.add_edge(u, v)
            nx.draw_networkx_edges(G, pos, ax=ax, edgelist=[(u, v)], width=2, arrows=True)
            
            edge_pos = ((pos[u][0] + pos[v][0])/2, (pos[u][1] + pos[v][1])/2)
            ax.text(edge_pos[0], edge_pos[1], label, fontsize=8, bbox=dict(facecolor='white', alpha=0.7))

        ax.set_title("Optimal Transport Flow")
        self.canvas.draw()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
