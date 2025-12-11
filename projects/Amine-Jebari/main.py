import sys
import string
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QGroupBox,
    QHeaderView
)
from PyQt6.QtCore import QThread, pyqtSignal
import gurobipy as gp
from gurobipy import GRB

# --- WORKER THREAD FOR GUROBI (Prevents GUI Freezing) ---
class OptimizationWorker(QThread):
    result_ready = pyqtSignal(object)
    error_occurred = pyqtSignal(str)

    def __init__(self, nodes, edges, incompatibilities):
        super().__init__()
        self.nodes = nodes                  # [{'id': 'A', 'cost': 10.0}, ...]
        self.edges = edges                  # [('A','B'), ('B','C'), ...]
        self.incompatibilities = incompatibilities # [('A', 'C'), ...]

    def run(self):
        try:
            m = gp.Model("Logic_Circuit_Optimization")
            m.Params.OutputFlag = 0

            gate_ids = [n["id"] for n in self.nodes]
            x = m.addVars(gate_ids, vtype=GRB.BINARY, name="x")

            # Objective: Minimize total cost
            m.setObjective(
                gp.quicksum(n["cost"] * x[n["id"]] for n in self.nodes),
                GRB.MINIMIZE
            )

            # Constraint 1: Coverage (Vertex Cover)
            for u, v in self.edges:
                m.addConstr(x[u] + x[v] >= 1, name=f"cover_{u}_{v}")

            # Constraint 2: Incompatibility (Mutual Exclusion)
            for u, v in self.incompatibilities:
                # Ensure u and v are actually in the variable set before adding constraint
                if u in x and v in x:
                    m.addConstr(x[u] + x[v] <= 1, name=f"conflict_{u}_{v}")

            m.optimize()

            if m.status == GRB.OPTIMAL:
                selected = [gid for gid in gate_ids if x[gid].X > 0.5]
                self.result_ready.emit((selected, m.objVal))
            elif m.status == GRB.INFEASIBLE:
                 self.error_occurred.emit("Infeasible: Constraints cannot be satisfied (Conflict blocking coverage).")
            else:
                self.error_occurred.emit(f"No optimal solution found (status={m.status}).")

        except gp.GurobiError as e:
            self.error_occurred.emit(f"Gurobi Error: {e}")
        except Exception as e:
            self.error_occurred.emit(f"Error: {e}")


# --- MAIN GUI WINDOW ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Projet RO - Prob 15: Circuit Gate Optimization")
        self.resize(1300, 900)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # LEFT PANEL: Inputs
        input_panel = QGroupBox("Configuration du Circuit")
        input_layout = QVBoxLayout()

        # 1. Gates table
        self.table_gates = QTableWidget(0, 2)
        self.table_gates.setHorizontalHeaderLabels(["Gate ID", "Cost (Weight)"])
        self.table_gates.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        input_layout.addWidget(QLabel("1. Définir les Portes (Sommets):"))
        input_layout.addWidget(self.table_gates)

        # 2. Wires table
        self.table_wires = QTableWidget(0, 2)
        self.table_wires.setHorizontalHeaderLabels(["From Gate", "To Gate"])
        self.table_wires.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        input_layout.addWidget(QLabel("2. Définir les Fils (Arêtes):"))
        input_layout.addWidget(self.table_wires)

        # 3. Incompatibilities table (NEW ADDITION)
        self.table_incomp = QTableWidget(0, 2)
        self.table_incomp.setHorizontalHeaderLabels(["Gate A", "Gate B"])
        self.table_incomp.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        input_layout.addWidget(QLabel("3. Définir les Incompatibilités (Conflits):"))
        input_layout.addWidget(self.table_incomp)

        # -- Buttons for Tables --
        
        # Add buttons
        btn_add_layout = QHBoxLayout()
        self.btn_add_gate = QPushButton("Ajouter Porte")
        self.btn_add_gate.clicked.connect(self.add_gate_row)
        
        self.btn_add_wire = QPushButton("Ajouter Fil")
        self.btn_add_wire.clicked.connect(self.add_wire_row)

        self.btn_add_incomp = QPushButton("Ajouter Conflit")
        self.btn_add_incomp.clicked.connect(self.add_incomp_row)

        btn_add_layout.addWidget(self.btn_add_gate)
        btn_add_layout.addWidget(self.btn_add_wire)
        btn_add_layout.addWidget(self.btn_add_incomp)
        input_layout.addLayout(btn_add_layout)

        # Delete buttons
        btn_del_layout = QHBoxLayout()
        self.btn_del_gate = QPushButton("Supprimer Porte")
        self.btn_del_gate.clicked.connect(self.delete_selected_gates)
        
        self.btn_del_wire = QPushButton("Supprimer Fil")
        self.btn_del_wire.clicked.connect(self.delete_selected_wires)

        self.btn_del_incomp = QPushButton("Supprimer Conflit")
        self.btn_del_incomp.clicked.connect(self.delete_selected_incomp)

        btn_del_layout.addWidget(self.btn_del_gate)
        btn_del_layout.addWidget(self.btn_del_wire)
        btn_del_layout.addWidget(self.btn_del_incomp)
        input_layout.addLayout(btn_del_layout)

        # Solve button
        self.btn_solve = QPushButton("OPTIMISER (Lancer Gurobi)")
        self.btn_solve.setStyleSheet(
            "background-color: #4CAF50; color: white; font-weight: bold; padding: 10px;"
        )
        self.btn_solve.clicked.connect(self.run_optimization)
        input_layout.addWidget(self.btn_solve)

        # Result label
        self.lbl_result = QLabel("Status: Prêt")
        self.lbl_result.setStyleSheet("font-size: 14px; margin-top: 10px;")
        input_layout.addWidget(self.lbl_result)

        input_panel.setLayout(input_layout)
        main_layout.addWidget(input_panel, 1)

        # RIGHT PANEL: Visualization
        viz_panel = QGroupBox("Visualisation du Graphe")
        viz_layout = QVBoxLayout()
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        viz_layout.addWidget(self.canvas)
        viz_panel.setLayout(viz_layout)
        main_layout.addWidget(viz_panel, 2)

        # Pre-load demo data
        self.load_demo_data()
        self.update_graph_viz([])

    # ------------- helpers -------------
    def _get_gate_ids_in_table(self):
        ids = []
        for r in range(self.table_gates.rowCount()):
            item = self.table_gates.item(r, 0)
            if item and item.text().strip():
                ids.append(item.text().strip())
        return ids

    def _next_gate_id(self):
        existing = set(self._get_gate_ids_in_table())
        letters = list(string.ascii_uppercase)
        for ch in letters:
            if ch not in existing:
                return ch
        k = 1
        while True:
            for ch in letters:
                candidate = f"{ch}{k}"
                if candidate not in existing:
                    return candidate
            k += 1

    # ------------- row operations -------------
    def add_gate_row(self):
        row = self.table_gates.rowCount()
        self.table_gates.insertRow(row)
        self.table_gates.setItem(row, 0, QTableWidgetItem(self._next_gate_id()))
        self.table_gates.setItem(row, 1, QTableWidgetItem("10"))

    def add_wire_row(self):
        gate_ids = self._get_gate_ids_in_table()
        u_default = gate_ids[0] if len(gate_ids) >= 1 else "A"
        v_default = gate_ids[1] if len(gate_ids) >= 2 else "B"
        row = self.table_wires.rowCount()
        self.table_wires.insertRow(row)
        self.table_wires.setItem(row, 0, QTableWidgetItem(u_default))
        self.table_wires.setItem(row, 1, QTableWidgetItem(v_default))

    def add_incomp_row(self):
        gate_ids = self._get_gate_ids_in_table()
        u_default = gate_ids[0] if len(gate_ids) >= 1 else ""
        v_default = gate_ids[2] if len(gate_ids) >= 3 else "" # Suggest C if available
        row = self.table_incomp.rowCount()
        self.table_incomp.insertRow(row)
        self.table_incomp.setItem(row, 0, QTableWidgetItem(u_default))
        self.table_incomp.setItem(row, 1, QTableWidgetItem(v_default))

    def delete_selected_gates(self):
        self._delete_rows(self.table_gates)

    def delete_selected_wires(self):
        self._delete_rows(self.table_wires)

    def delete_selected_incomp(self):
        self._delete_rows(self.table_incomp)

    def _delete_rows(self, table_widget):
        rows = sorted({idx.row() for idx in table_widget.selectedIndexes()}, reverse=True)
        if not rows:
            QMessageBox.information(self, "Info", "Sélectionnez une ou plusieurs lignes à supprimer.")
            return
        for r in rows:
            table_widget.removeRow(r)

    # ------------- demo data -------------
    def load_demo_data(self):
        self.table_gates.setRowCount(0)
        self.table_wires.setRowCount(0)
        self.table_incomp.setRowCount(0)

        # 1. Gates
        gates = [("A", "10"), ("B", "10"), ("C", "5")]
        for gid, cost in gates:
            row = self.table_gates.rowCount()
            self.table_gates.insertRow(row)
            self.table_gates.setItem(row, 0, QTableWidgetItem(gid))
            self.table_gates.setItem(row, 1, QTableWidgetItem(cost))

        # 2. Wires
        wires = [("A", "B"), ("B", "C"), ("C", "A")]
        for u, v in wires:
            row = self.table_wires.rowCount()
            self.table_wires.insertRow(row)
            self.table_wires.setItem(row, 0, QTableWidgetItem(u))
            self.table_wires.setItem(row, 1, QTableWidgetItem(v))
        
        # 3. Incompatibilities (Empty by default, user can add A-C to test)
        # To test automatically, uncomment below:
        # row = self.table_incomp.rowCount()
        # self.table_incomp.insertRow(row)
        # self.table_incomp.setItem(row, 0, QTableWidgetItem("A"))
        # self.table_incomp.setItem(row, 1, QTableWidgetItem("C"))

    # ------------- data extraction + validation -------------
    def get_data_from_ui(self):
        nodes = []
        edges = []
        incompatibilities = []

        try:
            # 1. Read gates
            for r in range(self.table_gates.rowCount()):
                item_id = self.table_gates.item(r, 0)
                item_cost = self.table_gates.item(r, 1)
                if item_id is None or item_cost is None: continue
                gid = item_id.text().strip()
                if not gid: continue
                cost = float(item_cost.text())
                nodes.append({"id": gid, "cost": cost})

            gate_ids = [n["id"] for n in nodes]
            if len(set(gate_ids)) != len(gate_ids):
                QMessageBox.warning(self, "Erreur", "Gate IDs dupliqués détectés.")
                return None, None, None
            gate_set = set(gate_ids)

            # 2. Read wires
            for r in range(self.table_wires.rowCount()):
                item_u = self.table_wires.item(r, 0)
                item_v = self.table_wires.item(r, 1)
                if item_u is None or item_v is None: continue
                u = item_u.text().strip()
                v = item_v.text().strip()
                if not u or not v: continue
                
                if u not in gate_set or v not in gate_set:
                    QMessageBox.warning(self, "Erreur", f"Le fil ({u},{v}) référence une porte inexistante.")
                    return None, None, None
                edges.append((u, v))

            # 3. Read Incompatibilities (NEW)
            for r in range(self.table_incomp.rowCount()):
                item_u = self.table_incomp.item(r, 0)
                item_v = self.table_incomp.item(r, 1)
                if item_u is None or item_v is None: continue
                u = item_u.text().strip()
                v = item_v.text().strip()
                if not u or not v: continue

                if u not in gate_set or v not in gate_set:
                    QMessageBox.warning(self, "Erreur", f"Le conflit ({u},{v}) référence une porte inexistante.")
                    return None, None, None
                incompatibilities.append((u, v))

        except ValueError:
            QMessageBox.warning(self, "Erreur", "Vérifiez que les coûts sont numériques.")
            return None, None, None

        return nodes, edges, incompatibilities

    # ------------- optimization -------------
    def run_optimization(self):
        data = self.get_data_from_ui()
        if not data or data[0] is None:
            return
        
        # Unpack all 3
        nodes, edges, incompatibilities = data

        self.btn_solve.setEnabled(False)
        self.lbl_result.setText("Status: Calcul en cours...")

        # Pass incompatibilities to the worker
        self.worker = OptimizationWorker(nodes, edges, incompatibilities)
        self.worker.result_ready.connect(self.handle_result)
        self.worker.error_occurred.connect(self.handle_error)
        self.worker.start()

    def handle_result(self, result):
        selected_nodes, obj_val = result
        self.btn_solve.setEnabled(True)

        res_text = (
            f"<b>Solution Optimale Trouvée:</b><br>"
            f"Coût Total: {obj_val}<br>"
            f"Portes sélectionnées: {selected_nodes}"
        )
        self.lbl_result.setText(res_text)
        self.update_graph_viz(selected_nodes)

    def handle_error(self, error_msg):
        self.btn_solve.setEnabled(True)
        self.lbl_result.setText(f"Erreur: {error_msg}")

    # ------------- visualization -------------
    def update_graph_viz(self, selected_nodes):
        self.figure.clear()
        
        # Get data properly unpacking the 3 items
        data = self.get_data_from_ui()
        if not data or data[0] is None:
            return
        nodes, edges, incompatibilities = data

        G = nx.Graph()
        for n in nodes:
            G.add_node(n["id"])
        for u, v in edges:
            G.add_edge(u, v)
        
        # Add conflict edges just for visualization (optional, dashed lines?)
        # For now, we stick to the wire graph to keep it clean, as per original requirement.

        pos = nx.spring_layout(G, seed=42) # Seed for consistent layout
        color_map = ["red" if n["id"] in selected_nodes else "lightblue" for n in nodes]

        ax = self.figure.add_subplot(111)
        nx.draw(
            G, pos, ax=ax, with_labels=True, node_color=color_map,
            node_size=800, font_weight="bold", edge_color="gray"
        )
        ax.set_title("Visualisation du Circuit (Rouge = Sélectionné)")
        self.canvas.draw()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
