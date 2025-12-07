import sys
import string
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QGroupBox
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
        self.incompatibilities = incompatibilities

    def run(self):
        try:
            m = gp.Model("Logic_Circuit_Optimization")
            m.Params.OutputFlag = 0

            gate_ids = [n["id"] for n in self.nodes]
            x = m.addVars(gate_ids, vtype=GRB.BINARY, name="x")

            m.setObjective(
                gp.quicksum(n["cost"] * x[n["id"]] for n in self.nodes),
                GRB.MINIMIZE
            )

            for u, v in self.edges:
                m.addConstr(x[u] + x[v] >= 1, name=f"cover_{u}_{v}")

            for u, v in self.incompatibilities:
                if u in x and v in x:
                    m.addConstr(x[u] + x[v] <= 1, name=f"conflict_{u}_{v}")

            m.optimize()

            if m.status == GRB.OPTIMAL:
                selected = [gid for gid in gate_ids if x[gid].X > 0.5]
                self.result_ready.emit((selected, m.objVal))
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
        self.resize(1200, 800)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # LEFT PANEL
        input_panel = QGroupBox("Configuration du Circuit")
        input_layout = QVBoxLayout()

        # Gates table
        self.table_gates = QTableWidget(0, 2)
        self.table_gates.setHorizontalHeaderLabels(["Gate ID", "Cost (Weight)"])
        self.table_gates.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        input_layout.addWidget(QLabel("1. Définir les Portes (Sommets):"))
        input_layout.addWidget(self.table_gates)

        # Wires table
        self.table_wires = QTableWidget(0, 2)
        self.table_wires.setHorizontalHeaderLabels(["From Gate", "To Gate"])
        self.table_wires.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        input_layout.addWidget(QLabel("2. Définir les Fils (Arêtes):"))
        input_layout.addWidget(self.table_wires)

        # Add buttons
        btn_add_layout = QHBoxLayout()
        self.btn_add_gate = QPushButton("Ajouter Porte")
        self.btn_add_gate.clicked.connect(self.add_gate_row)
        self.btn_add_wire = QPushButton("Ajouter Fil")
        self.btn_add_wire.clicked.connect(self.add_wire_row)
        btn_add_layout.addWidget(self.btn_add_gate)
        btn_add_layout.addWidget(self.btn_add_wire)
        input_layout.addLayout(btn_add_layout)

        # Delete buttons
        btn_del_layout = QHBoxLayout()
        self.btn_del_gate = QPushButton("Supprimer Porte(s)")
        self.btn_del_gate.clicked.connect(self.delete_selected_gates)
        self.btn_del_wire = QPushButton("Supprimer Fil(s)")
        self.btn_del_wire.clicked.connect(self.delete_selected_wires)
        btn_del_layout.addWidget(self.btn_del_gate)
        btn_del_layout.addWidget(self.btn_del_wire)
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
        """Generate A, B, C... then A1, B1... if needed."""
        existing = set(self._get_gate_ids_in_table())
        letters = list(string.ascii_uppercase)

        # Try single letters first
        for ch in letters:
            if ch not in existing:
                return ch

        # Then A1..Z1, A2..Z2, ...
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
        self.table_gates.setItem(row, 1, QTableWidgetItem("10"))  # default cost

    def add_wire_row(self):
        gate_ids = self._get_gate_ids_in_table()
        u_default = gate_ids[0] if len(gate_ids) >= 1 else "A"
        v_default = gate_ids[1] if len(gate_ids) >= 2 else "B"

        row = self.table_wires.rowCount()
        self.table_wires.insertRow(row)
        self.table_wires.setItem(row, 0, QTableWidgetItem(u_default))
        self.table_wires.setItem(row, 1, QTableWidgetItem(v_default))

    def delete_selected_gates(self):
        rows = sorted({idx.row() for idx in self.table_gates.selectedIndexes()}, reverse=True)
        if not rows:
            QMessageBox.information(self, "Info", "Sélectionnez une ou plusieurs lignes dans la table des Portes.")
            return
        for r in rows:
            self.table_gates.removeRow(r)

    def delete_selected_wires(self):
        rows = sorted({idx.row() for idx in self.table_wires.selectedIndexes()}, reverse=True)
        if not rows:
            QMessageBox.information(self, "Info", "Sélectionnez une ou plusieurs lignes dans la table des Fils.")
            return
        for r in rows:
            self.table_wires.removeRow(r)

    # ------------- demo data -------------
    def load_demo_data(self):
        # Clear current
        self.table_gates.setRowCount(0)
        self.table_wires.setRowCount(0)

        # Gates A..E
        for gid in ["A", "B", "C", "D", "E"]:
            row = self.table_gates.rowCount()
            self.table_gates.insertRow(row)
            self.table_gates.setItem(row, 0, QTableWidgetItem(gid))
            self.table_gates.setItem(row, 1, QTableWidgetItem("10"))

        # Wires (same structure as before, but with letters)
        wires = [("A", "B"), ("B", "C"), ("C", "D"), ("D", "E"), ("A", "E"), ("B", "D")]
        for u, v in wires:
            row = self.table_wires.rowCount()
            self.table_wires.insertRow(row)
            self.table_wires.setItem(row, 0, QTableWidgetItem(u))
            self.table_wires.setItem(row, 1, QTableWidgetItem(v))

    # ------------- data extraction + validation -------------
    def get_data_from_ui(self):
        nodes = []
        edges = []

        try:
            # Read gates
            for r in range(self.table_gates.rowCount()):
                item_id = self.table_gates.item(r, 0)
                item_cost = self.table_gates.item(r, 1)
                if item_id is None or item_cost is None:
                    raise ValueError("Missing gate cell.")
                gid = item_id.text().strip()
                if not gid:
                    raise ValueError("Empty gate ID.")
                cost = float(item_cost.text())
                nodes.append({"id": gid, "cost": cost})

            gate_ids = [n["id"] for n in nodes]
            if len(set(gate_ids)) != len(gate_ids):
                QMessageBox.warning(self, "Erreur", "Gate IDs dupliqués détectés. Chaque Gate ID doit être unique.")
                return None, None
            gate_set = set(gate_ids)

            # Read wires
            for r in range(self.table_wires.rowCount()):
                item_u = self.table_wires.item(r, 0)
                item_v = self.table_wires.item(r, 1)
                if item_u is None or item_v is None:
                    raise ValueError("Missing wire cell.")
                u = item_u.text().strip()
                v = item_v.text().strip()
                if not u or not v:
                    raise ValueError("Empty wire endpoint.")
                if u == v:
                    QMessageBox.warning(self, "Erreur", f"Fil invalide (boucle) à la ligne {r+1}: ({u},{v}).")
                    return None, None
                if u not in gate_set or v not in gate_set:
                    QMessageBox.warning(
                        self, "Erreur",
                        f"Le fil ({u},{v}) référence une porte inexistante. Ajoutez la porte ou corrigez le fil."
                    )
                    return None, None
                edges.append((u, v))

        except ValueError:
            QMessageBox.warning(self, "Erreur", "Vérifiez que tous les champs sont remplis et les coûts numériques.")
            return None, None

        return nodes, edges

    # ------------- optimization -------------
    def run_optimization(self):
        nodes, edges = self.get_data_from_ui()
        if not nodes:
            return

        self.btn_solve.setEnabled(False)
        self.lbl_result.setText("Status: Calcul en cours...")

        self.worker = OptimizationWorker(nodes, edges, [])
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
        nodes, edges = self.get_data_from_ui()
        if not nodes:
            return

        G = nx.Graph()
        for n in nodes:
            G.add_node(n["id"])
        for u, v in edges:
            G.add_edge(u, v)

        pos = nx.spring_layout(G)

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
