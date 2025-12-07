import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QGraphicsView,
    QGraphicsScene, QGraphicsEllipseItem, QGraphicsLineItem,
    QListWidget, QMessageBox, QComboBox, QGraphicsTextItem
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPen, QBrush, QFont
from gurobipy import Model, GRB 

class DraggableNode(QGraphicsEllipseItem):
    def __init__(self, x, y, name, parent_gui, radius=30):
        super().__init__(-radius/2, -radius/2, radius, radius) 
        self.parent_gui = parent_gui
        self.name = name
        self.radius = radius
        self.setPos(x, y) 
        self.setBrush(QBrush(Qt.GlobalColor.white))
        self.setPen(QPen(Qt.GlobalColor.black, 2))
        self.setZValue(10) 
        self.setFlags(
            QGraphicsEllipseItem.GraphicsItemFlag.ItemIsMovable |
            QGraphicsEllipseItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )
        self.label = QGraphicsTextItem(name, self)
        font = QFont()
        font.setBold(True)
        font.setPointSize(12)
        self.label.setFont(font)
        self.label.setDefaultTextColor(Qt.GlobalColor.black)
        label_rect = self.label.boundingRect()
        self.label.setPos(-label_rect.width()/2, -label_rect.height()/2)

    def itemChange(self, change, value):
        if change == QGraphicsEllipseItem.GraphicsItemChange.ItemPositionChange:
            if self.parent_gui:
                self.parent_gui.update_arcs_for_node(self.name)
        return super().itemChange(change, value)
    
    def get_center(self):
        return self.pos()

class Node:
    def __init__(self, name, graphic_item):
        self.name = name
        self.graphic_item = graphic_item

class Arc:
    def __init__(self, from_node, to_node, capacity):
        self.from_node = from_node
        self.to_node = to_node
        self.capacity = capacity
        self.flow = 0
        self.line_item = None
        self.label_item = None

class MaxFlowGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dynamic Max Flow GUI")
        self.setGeometry(50, 50, 900, 600)
        self.nodes = {}
        self.arcs = []
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.control_layout = QVBoxLayout()
        self.layout.addLayout(self.control_layout, 1)
        self.node_input = QLineEdit()
        self.node_input.setPlaceholderText("Node name")
        self.control_layout.addWidget(self.node_input)
        self.add_node_btn = QPushButton("Add Node")
        self.add_node_btn.clicked.connect(self.add_node)
        self.control_layout.addWidget(self.add_node_btn)
        self.source_combo = QComboBox()
        self.source_combo.addItem("Select source")
        self.control_layout.addWidget(QLabel("Source Node:"))
        self.control_layout.addWidget(self.source_combo)
        self.sink_combo = QComboBox()
        self.sink_combo.addItem("Select sink")
        self.control_layout.addWidget(QLabel("Sink Node:"))
        self.control_layout.addWidget(self.sink_combo)
        self.from_node_input = QLineEdit()
        self.from_node_input.setPlaceholderText("From node")
        self.control_layout.addWidget(self.from_node_input)
        self.to_node_input = QLineEdit()
        self.to_node_input.setPlaceholderText("To node")
        self.control_layout.addWidget(self.to_node_input)
        self.capacity_input = QLineEdit()
        self.capacity_input.setPlaceholderText("Capacity")
        self.control_layout.addWidget(self.capacity_input)
        self.add_arc_btn = QPushButton("Add Arc")
        self.add_arc_btn.clicked.connect(self.add_arc)
        self.control_layout.addWidget(self.add_arc_btn)
        self.solve_btn = QPushButton("Solve Max Flow")
        self.solve_btn.clicked.connect(self.solve_max_flow)
        self.control_layout.addWidget(self.solve_btn)
        self.result_label = QLabel("Maximum Flow: ")
        self.control_layout.addWidget(self.result_label)
        self.flow_list = QListWidget()
        self.control_layout.addWidget(self.flow_list)
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.layout.addWidget(self.view, 2)

    def add_node(self):
        name = self.node_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "Node name cannot be empty")
            return
        if name in self.nodes:
            QMessageBox.warning(self, "Error", "Node already exists")
            return
        view_rect = self.view.viewport().rect()
        view_center = view_rect.center()
        scene_center = self.view.mapToScene(view_center)
        x = scene_center.x()
        y = scene_center.y()
        node_item = DraggableNode(x, y, name, self) 
        self.scene.addItem(node_item)
        self.nodes[name] = Node(name, node_item)
        self.source_combo.addItem(name)
        self.sink_combo.addItem(name)
        self.node_input.clear()

    def add_arc(self):
        from_name = self.from_node_input.text().strip()
        to_name = self.to_node_input.text().strip()
        try:
            capacity = float(self.capacity_input.text())
        except:
            QMessageBox.warning(self, "Error", "Capacity must be a number")
            return
        if from_name not in self.nodes or to_name not in self.nodes:
            QMessageBox.warning(self, "Error", "Both nodes must exist")
            return
        arc = Arc(from_name, to_name, capacity)
        self.arcs.append(arc)
        n1 = self.nodes[from_name].graphic_item
        n2 = self.nodes[to_name].graphic_item
        center1 = n1.get_center()
        center2 = n2.get_center()
        line = QGraphicsLineItem(center1.x(), center1.y(), center2.x(), center2.y())
        pen = QPen(Qt.GlobalColor.black)
        pen.setWidth(2)
        line.setPen(pen)
        self.scene.addItem(line)
        mid_x = (center1.x() + center2.x()) / 2
        mid_y = (center1.y() + center2.y()) / 2
        label_item = self.scene.addText(f"{capacity}")
        font = QFont()
        font.setBold(True)
        font.setPointSize(10)
        label_item.setFont(font)
        label_item.setDefaultTextColor(Qt.GlobalColor.blue) 
        label_rect = label_item.boundingRect()
        label_item.setPos(mid_x, mid_y - label_rect.height()) 
        label_item.setZValue(5) 
        arc.line_item = line
        arc.label_item = label_item
        self.from_node_input.clear()
        self.to_node_input.clear()
        self.capacity_input.clear()

    def update_arcs_for_node(self, node_name):
        moved_node = self.nodes.get(node_name)
        if not moved_node:
            return
        new_center = moved_node.graphic_item.get_center()
        for arc in self.arcs:
            is_from_node = (arc.from_node == node_name)
            is_to_node = (arc.to_node == node_name)
            if is_from_node or is_to_node:
                n1 = self.nodes[arc.from_node].graphic_item
                n2 = self.nodes[arc.to_node].graphic_item
                start_center = new_center if is_from_node else n1.get_center()
                end_center = new_center if is_to_node else n2.get_center()
                arc.line_item.setLine(
                    start_center.x(), start_center.y(), 
                    end_center.x(), end_center.y()
                )
                mid_x = (start_center.x() + end_center.x()) / 2
                mid_y = (start_center.y() + end_center.y()) / 2
                label_rect = arc.label_item.boundingRect()
                arc.label_item.setPos(mid_x, mid_y - label_rect.height()) 

    def solve_max_flow(self):
        if not self.nodes or not self.arcs:
            QMessageBox.warning(self, "Error", "Add nodes and arcs first")
            return
        source = self.source_combo.currentText()
        sink = self.sink_combo.currentText()
        if source == "Select source" or sink == "Select sink":
            QMessageBox.warning(self, "Error", "Select valid source and sink")
            return
        m = Model("max_flow")
        f = {}
        capacities = {(arc.from_node, arc.to_node): arc.capacity for arc in self.arcs}
        for (i, j), cap in capacities.items():
            f[i, j] = m.addVar(lb=0, ub=cap, name=f"f_{i}_{j}")
        m.setObjective(sum(f[i, j] for (i, j) in capacities if i == source), GRB.MAXIMIZE)
        for k in self.nodes:
            if k in [source, sink]:
                continue
            inflow = sum(f[i, j] for (i, j) in capacities if j == k)
            outflow = sum(f[i, j] for (i, j) in capacities if i == k)
            m.addConstr(inflow == outflow)
        m.optimize()
        if m.status == GRB.OPTIMAL:
            self.result_label.setText(f"Maximum Flow: {m.objVal}")
            self.flow_list.clear()
            for arc in self.arcs:
                arc.flow = f[arc.from_node, arc.to_node].X
                self.flow_list.addItem(f"{arc.from_node} -> {arc.to_node}: {arc.flow:.2f} / {arc.capacity:.2f}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MaxFlowGUI()
    window.show()
    sys.exit(app.exec())
