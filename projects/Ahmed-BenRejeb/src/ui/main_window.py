"""
Interface utilisateur principale pour l'application de mélange d'alliages.

Cette interface permet la saisie des données, la résolution et l'affichage des résultats
en utilisant PyQt5 avec des composants professionnels.
"""

import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QTableWidget, QTableWidgetItem, QPushButton, QLabel,
    QLineEdit, QSpinBox, QDoubleSpinBox, QGroupBox, QFormLayout,
    QTextEdit, QProgressBar, QMessageBox, QFileDialog, QComboBox,
    QSplitter, QFrame, QScrollArea, QGridLayout, QHeaderView
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QPixmap, QPalette, QColor, QIcon
import traceback
import json
from typing import Dict, List, Optional

# Import des modèles avec gestion des paths
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from models import (
    BlendingProblem, RawMaterial, AlloySpecification, Element,
    BlendingOptimizer, OptimizationResult
)


class OptimizationThread(QThread):
    """Thread pour l'exécution non-bloquante de l'optimisation."""
    
    finished = pyqtSignal(OptimizationResult)
    progress = pyqtSignal(str)  # Messages de progression
    error = pyqtSignal(str)     # Messages d'erreur
    
    def __init__(self, problem: BlendingProblem):
        super().__init__()
        self.problem = problem
        
    def run(self):
        """Exécute l'optimisation dans un thread séparé."""
        try:
            self.progress.emit("Initialisation du modèle d'optimisation...")
            optimizer = BlendingOptimizer(self.problem)
            
            self.progress.emit("Construction du modèle Gurobi...")
            optimizer.build_model()
            
            self.progress.emit("Résolution en cours...")
            result = optimizer.solve()
            
            # Analyse de sensibilité si solution optimale
            if result.status == "OPTIMAL":
                self.progress.emit("Analyse de sensibilité...")
                result.sensitivity_analysis = optimizer.perform_sensitivity_analysis()
            
            self.progress.emit("Optimisation terminée!")
            self.finished.emit(result)
            
        except Exception as e:
            self.error.emit(f"Erreur lors de l'optimisation: {str(e)}\n{traceback.format_exc()}")


class MaterialTableWidget(QTableWidget):
    """Widget de table personnalisé pour la saisie des matières premières."""
    
    def __init__(self):
        super().__init__()
        self.setup_table()
        
    def setup_table(self):
        """Configure la table des matières premières."""
        headers = ["Nom", "Coût (€/kg)", "Disponibilité (kg)", "Densité", "Pureté (%)", "Composition"]
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)
        
        # Configuration de l'affichage
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.horizontalHeader().setStretchLastSection(True)
        self.setMinimumHeight(200)
        
        # Ajouter quelques lignes par défaut
        self.setRowCount(5)
        for i in range(5):
            self.add_material_row(i)
    
    def add_material_row(self, row: int):
        """Ajoute une ligne pour une matière première."""
        # Nom
        name_item = QTableWidgetItem("")
        self.setItem(row, 0, name_item)
        
        # Coût
        cost_item = QTableWidgetItem("0.0")
        self.setItem(row, 1, cost_item)
        
        # Disponibilité
        availability_item = QTableWidgetItem("1000.0")
        self.setItem(row, 2, availability_item)
        
        # Densité
        density_item = QTableWidgetItem("7.8")
        self.setItem(row, 3, density_item)
        
        # Pureté
        purity_item = QTableWidgetItem("100.0")
        self.setItem(row, 4, purity_item)
        
        # Composition (format JSON simple)
        composition_item = QTableWidgetItem("{}")
        self.setItem(row, 5, composition_item)
    
    def add_row(self):
        """Ajoute une nouvelle ligne à la table."""
        row_count = self.rowCount()
        self.setRowCount(row_count + 1)
        self.add_material_row(row_count)
    
    def remove_selected_row(self):
        """Supprime la ligne sélectionnée."""
        current_row = self.currentRow()
        if current_row >= 0:
            self.removeRow(current_row)
    
    def get_materials(self) -> List[RawMaterial]:
        """Extrait les matières premières de la table."""
        materials = []
        
        for row in range(self.rowCount()):
            name_item = self.item(row, 0)
            if name_item is None or not name_item.text().strip():
                continue
                
            try:
                name = name_item.text().strip()
                cost = float(self.item(row, 1).text())
                availability = float(self.item(row, 2).text())
                density = float(self.item(row, 3).text())
                purity = float(self.item(row, 4).text())
                
                # Parse composition JSON
                composition_text = self.item(row, 5).text().strip()
                if composition_text:
                    composition = json.loads(composition_text)
                else:
                    composition = {}
                
                material = RawMaterial(
                    name=name,
                    cost_per_kg=cost,
                    availability=availability,
                    composition=composition,
                    density=density,
                    purity=purity
                )
                materials.append(material)
                
            except (ValueError, json.JSONDecodeError) as e:
                # Ignorer les lignes avec des erreurs
                continue
        
        return materials


class ElementSpecWidget(QWidget):
    """Widget pour la spécification des éléments chimiques."""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        """Configure l'interface de spécification des éléments."""
        layout = QVBoxLayout(self)
        
        # Titre
        title = QLabel("Spécifications des Éléments Chimiques")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title)
        
        # Table des éléments
        self.elements_table = QTableWidget()
        headers = ["Symbole", "Nom", "Min (%)", "Max (%)", "Cible (%)", "Actif"]
        self.elements_table.setColumnCount(len(headers))
        self.elements_table.setHorizontalHeaderLabels(headers)
        self.elements_table.setAlternatingRowColors(True)
        self.elements_table.horizontalHeader().setStretchLastSection(True)
        
        # Ajouter des éléments communs
        common_elements = [
            ("Fe", "Fer", 0.0, 100.0, None),
            ("C", "Carbone", 0.0, 2.0, None),
            ("Ni", "Nickel", 0.0, 25.0, None),
            ("Cr", "Chrome", 0.0, 30.0, None),
            ("Mn", "Manganèse", 0.0, 2.0, None),
            ("Si", "Silicium", 0.0, 1.0, None),
            ("Mo", "Molybdène", 0.0, 5.0, None),
            ("Al", "Aluminium", 0.0, 10.0, None)
        ]
        
        self.elements_table.setRowCount(len(common_elements))
        for i, (symbol, name, min_val, max_val, target) in enumerate(common_elements):
            self.elements_table.setItem(i, 0, QTableWidgetItem(symbol))
            self.elements_table.setItem(i, 1, QTableWidgetItem(name))
            self.elements_table.setItem(i, 2, QTableWidgetItem(str(min_val)))
            self.elements_table.setItem(i, 3, QTableWidgetItem(str(max_val)))
            self.elements_table.setItem(i, 4, QTableWidgetItem(str(target) if target else ""))
            
            # Case à cocher pour activer/désactiver
            checkbox_item = QTableWidgetItem()
            checkbox_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            checkbox_item.setCheckState(Qt.Unchecked)
            self.elements_table.setItem(i, 5, checkbox_item)
        
        layout.addWidget(self.elements_table)
        
        # Boutons de contrôle
        buttons_layout = QHBoxLayout()
        
        add_btn = QPushButton("Ajouter Élément")
        add_btn.clicked.connect(self.add_element)
        buttons_layout.addWidget(add_btn)
        
        remove_btn = QPushButton("Supprimer")
        remove_btn.clicked.connect(self.remove_element)
        buttons_layout.addWidget(remove_btn)
        
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)
    
    def add_element(self):
        """Ajoute un nouvel élément."""
        row_count = self.elements_table.rowCount()
        self.elements_table.setRowCount(row_count + 1)
        
        # Valeurs par défaut
        for col in range(5):
            self.elements_table.setItem(row_count, col, QTableWidgetItem(""))
        
        # Case à cocher
        checkbox_item = QTableWidgetItem()
        checkbox_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
        checkbox_item.setCheckState(Qt.Unchecked)
        self.elements_table.setItem(row_count, 5, checkbox_item)
    
    def remove_element(self):
        """Supprime l'élément sélectionné."""
        current_row = self.elements_table.currentRow()
        if current_row >= 0:
            self.elements_table.removeRow(current_row)
    
    def get_elements(self) -> List[Element]:
        """Extrait les éléments actifs de la table."""
        elements = []
        
        for row in range(self.elements_table.rowCount()):
            # Vérifier si l'élément est actif
            checkbox_item = self.elements_table.item(row, 5)
            if checkbox_item and checkbox_item.checkState() == Qt.Checked:
                try:
                    symbol = self.elements_table.item(row, 0).text().strip()
                    name = self.elements_table.item(row, 1).text().strip()
                    min_percent = float(self.elements_table.item(row, 2).text())
                    max_percent = float(self.elements_table.item(row, 3).text())
                    
                    target_text = self.elements_table.item(row, 4).text().strip()
                    target_percent = float(target_text) if target_text else None
                    
                    if symbol and name:
                        element = Element(
                            symbol=symbol,
                            name=name,
                            min_percent=min_percent,
                            max_percent=max_percent,
                            target_percent=target_percent
                        )
                        elements.append(element)
                
                except (ValueError, AttributeError):
                    continue
        
        return elements


class AlloyMainWindow(QMainWindow):
    """Fenêtre principale de l'application."""
    
    def __init__(self):
        super().__init__()
        self.problem = None
        self.optimization_thread = None
        self.result = None
        self.setup_ui()
        self.setup_style()
        
    def setup_ui(self):
        """Configure l'interface utilisateur principale."""
        self.setWindowTitle("Optimisation de Mélange d'Alliages Métallurgiques")
        self.setMinimumSize(1200, 800)
        
        # Widget central avec onglets
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Barre d'outils supérieure
        self.create_toolbar(layout)
        
        # Onglets principaux
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Onglet 1: Configuration du problème
        self.create_problem_tab()
        
        # Onglet 2: Résolution et résultats
        self.create_results_tab()
        
        # Onglet 3: Visualisation
        self.create_visualization_tab()
        
        # Barre de statut
        self.statusBar().showMessage("Prêt")
        
        # Vérifier si Gurobi est disponible
        try:
            import gurobipy
            self.gurobi_available = True
        except ImportError:
            self.gurobi_available = False
            self.statusBar().showMessage("Mode simulation - Gurobi non disponible (l'interface fonctionne normalement)")
            
            # Ajouter une note d'information
            info_label = QLabel("ℹ️ Mode Simulation: L'interface fonctionne sans Gurobi avec des résultats fictifs pour la démonstration")
            info_label.setStyleSheet("QLabel { background-color: #fffacd; color: #856404; padding: 5px; border: 1px solid #ffeaa7; border-radius: 3px; }")
            layout.addWidget(info_label)
        
    def create_toolbar(self, layout):
        """Crée la barre d'outils supérieure."""
        toolbar_frame = QFrame()
        toolbar_frame.setFrameStyle(QFrame.StyledPanel)
        toolbar_layout = QHBoxLayout(toolbar_frame)
        
        # Boutons principaux
        self.load_btn = QPushButton("📂 Charger")
        self.load_btn.clicked.connect(self.load_problem)
        toolbar_layout.addWidget(self.load_btn)
        
        self.save_btn = QPushButton("💾 Sauvegarder")
        self.save_btn.clicked.connect(self.save_problem)
        toolbar_layout.addWidget(self.save_btn)
        
        toolbar_layout.addWidget(QFrame())  # Séparateur
        
        self.solve_btn = QPushButton("🚀 Optimiser")
        self.solve_btn.clicked.connect(self.start_optimization)
        self.solve_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; }")
        toolbar_layout.addWidget(self.solve_btn)
        
        self.stop_btn = QPushButton("⏹ Arrêter")
        self.stop_btn.clicked.connect(self.stop_optimization)
        self.stop_btn.setEnabled(False)
        toolbar_layout.addWidget(self.stop_btn)
        
        toolbar_layout.addStretch()
        
        # Barre de progression
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        toolbar_layout.addWidget(self.progress_bar)
        
        layout.addWidget(toolbar_frame)
    
    def create_problem_tab(self):
        """Crée l'onglet de configuration du problème."""
        problem_widget = QWidget()
        layout = QVBoxLayout(problem_widget)
        
        # Splitter horizontal pour diviser en zones
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)
        
        # Zone gauche: Configuration générale
        config_group = QGroupBox("Configuration Générale")
        config_layout = QFormLayout(config_group)
        
        self.problem_name_edit = QLineEdit("Mélange d'Alliage Métallurgique")
        config_layout.addRow("Nom du Problème:", self.problem_name_edit)
        
        self.alloy_name_edit = QLineEdit("Acier Inoxydable 316L")
        config_layout.addRow("Type d'Alliage:", self.alloy_name_edit)
        
        self.target_weight_spin = QDoubleSpinBox()
        self.target_weight_spin.setRange(1.0, 100000.0)
        self.target_weight_spin.setValue(1000.0)
        self.target_weight_spin.setSuffix(" kg")
        config_layout.addRow("Poids Cible:", self.target_weight_spin)
        
        self.max_impurities_spin = QDoubleSpinBox()
        self.max_impurities_spin.setRange(0.0, 10.0)
        self.max_impurities_spin.setValue(2.0)
        self.max_impurities_spin.setSuffix(" %")
        config_layout.addRow("Impuretés Max:", self.max_impurities_spin)
        
        splitter.addWidget(config_group)
        
        # Zone droite: Spécifications des éléments
        self.element_spec_widget = ElementSpecWidget()
        splitter.addWidget(self.element_spec_widget)
        
        # Zone bas: Table des matières premières
        materials_group = QGroupBox("Matières Premières Disponibles")
        materials_layout = QVBoxLayout(materials_group)
        
        self.materials_table = MaterialTableWidget()
        materials_layout.addWidget(self.materials_table)
        
        # Boutons pour les matières premières
        materials_buttons = QHBoxLayout()
        
        add_material_btn = QPushButton("Ajouter Matière Première")
        add_material_btn.clicked.connect(self.materials_table.add_row)
        materials_buttons.addWidget(add_material_btn)
        
        remove_material_btn = QPushButton("Supprimer")
        remove_material_btn.clicked.connect(self.materials_table.remove_selected_row)
        materials_buttons.addWidget(remove_material_btn)
        
        load_preset_btn = QPushButton("Charger Preset Acier")
        load_preset_btn.clicked.connect(self.load_steel_preset)
        materials_buttons.addWidget(load_preset_btn)
        
        materials_buttons.addStretch()
        materials_layout.addLayout(materials_buttons)
        
        layout.addWidget(materials_group)
        
        self.tab_widget.addTab(problem_widget, "🔧 Configuration")
    
    def create_results_tab(self):
        """Crée l'onglet des résultats."""
        results_widget = QWidget()
        layout = QVBoxLayout(results_widget)
        
        # Splitter vertical
        splitter = QSplitter(Qt.Vertical)
        layout.addWidget(splitter)
        
        # Zone supérieure: Résumé des résultats
        summary_group = QGroupBox("Résumé de l'Optimisation")
        summary_layout = QFormLayout(summary_group)
        
        self.status_label = QLabel("Non résolu")
        summary_layout.addRow("Statut:", self.status_label)
        
        self.objective_label = QLabel("N/A")
        summary_layout.addRow("Coût Total Optimal:", self.objective_label)
        
        self.solve_time_label = QLabel("N/A")
        summary_layout.addRow("Temps de Résolution:", self.solve_time_label)
        
        self.total_weight_label = QLabel("N/A")
        summary_layout.addRow("Poids Total:", self.total_weight_label)
        
        splitter.addWidget(summary_group)
        
        # Zone du milieu: Solution détaillée
        solution_group = QGroupBox("Solution Détaillée")
        solution_layout = QVBoxLayout(solution_group)
        
        self.solution_table = QTableWidget()
        self.solution_table.setColumnCount(4)
        self.solution_table.setHorizontalHeaderLabels(["Matière Première", "Quantité (kg)", "Coût (€)", "Pourcentage"])
        self.solution_table.horizontalHeader().setStretchLastSection(True)
        solution_layout.addWidget(self.solution_table)
        
        splitter.addWidget(solution_group)
        
        # Zone inférieure: Composition finale
        composition_group = QGroupBox("Composition Chimique Finale")
        composition_layout = QVBoxLayout(composition_group)
        
        self.composition_table = QTableWidget()
        self.composition_table.setColumnCount(4)
        self.composition_table.setHorizontalHeaderLabels(["Élément", "Pourcentage (%)", "Min Requis (%)", "Max Autorisé (%)"])
        self.composition_table.horizontalHeader().setStretchLastSection(True)
        composition_layout.addWidget(self.composition_table)
        
        splitter.addWidget(composition_group)
        
        self.tab_widget.addTab(results_widget, "📊 Résultats")
    
    def create_visualization_tab(self):
        """Crée l'onglet de visualisation."""
        from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
        from matplotlib.figure import Figure
        
        viz_widget = QWidget()
        layout = QVBoxLayout(viz_widget)
        
        # Options de visualisation
        controls_layout = QHBoxLayout()
        
        self.viz_type_combo = QComboBox()
        self.viz_type_combo.addItems([
            "Répartition des Matières Premières",
            "Composition Chimique",
            "Analyse des Contraintes",
            "Coûts par Composant"
        ])
        self.viz_type_combo.currentTextChanged.connect(self.update_visualization)
        controls_layout.addWidget(QLabel("Type de Graphique:"))
        controls_layout.addWidget(self.viz_type_combo)
        
        update_viz_btn = QPushButton("🔄 Actualiser")
        update_viz_btn.clicked.connect(self.update_visualization)
        controls_layout.addWidget(update_viz_btn)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Canvas matplotlib
        self.figure = Figure(figsize=(12, 8))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
        self.tab_widget.addTab(viz_widget, "📈 Visualisation")
    
    def setup_style(self):
        """Configure le style de l'application."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QTableWidget {
                gridline-color: #d0d0d0;
                selection-background-color: #3daee9;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QPushButton {
                padding: 8px 16px;
                border-radius: 4px;
                border: 1px solid #cccccc;
                background-color: #ffffff;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
        """)
    
    def load_steel_preset(self):
        """Charge un preset pour l'acier inoxydable."""
        # Effacer la table actuelle
        self.materials_table.setRowCount(0)
        
        # Données de matières premières typiques pour l'acier inoxydable
        steel_materials = [
            {
                "name": "Ferraille Inox 316",
                "cost": 2.5,
                "availability": 5000,
                "density": 8.0,
                "purity": 98.0,
                "composition": {"Fe": 65.0, "Cr": 17.0, "Ni": 12.0, "Mo": 2.5, "C": 0.03, "Mn": 2.0}
            },
            {
                "name": "Ferrochrome",
                "cost": 1.8,
                "availability": 2000,
                "density": 6.8,
                "purity": 95.0,
                "composition": {"Cr": 50.0, "Fe": 40.0, "C": 8.0, "Si": 1.5}
            },
            {
                "name": "Nickel Pur",
                "cost": 15.0,
                "availability": 1000,
                "density": 8.9,
                "purity": 99.9,
                "composition": {"Ni": 99.9}
            },
            {
                "name": "Molybdène",
                "cost": 25.0,
                "availability": 200,
                "density": 10.3,
                "purity": 99.5,
                "composition": {"Mo": 99.5}
            },
            {
                "name": "Fonte de Fer",
                "cost": 0.5,
                "availability": 10000,
                "density": 7.2,
                "purity": 96.0,
                "composition": {"Fe": 94.0, "C": 3.5, "Si": 2.0, "Mn": 0.5}
            }
        ]
        
        # Remplir la table
        self.materials_table.setRowCount(len(steel_materials))
        for i, material in enumerate(steel_materials):
            self.materials_table.setItem(i, 0, QTableWidgetItem(material["name"]))
            self.materials_table.setItem(i, 1, QTableWidgetItem(str(material["cost"])))
            self.materials_table.setItem(i, 2, QTableWidgetItem(str(material["availability"])))
            self.materials_table.setItem(i, 3, QTableWidgetItem(str(material["density"])))
            self.materials_table.setItem(i, 4, QTableWidgetItem(str(material["purity"])))
            self.materials_table.setItem(i, 5, QTableWidgetItem(json.dumps(material["composition"])))
        
        # Activer les éléments correspondants
        elements_to_activate = ["Fe", "Cr", "Ni", "Mo", "C", "Mn"]
        for row in range(self.element_spec_widget.elements_table.rowCount()):
            symbol_item = self.element_spec_widget.elements_table.item(row, 0)
            if symbol_item and symbol_item.text() in elements_to_activate:
                checkbox_item = self.element_spec_widget.elements_table.item(row, 5)
                if checkbox_item:
                    checkbox_item.setCheckState(Qt.Checked)
        
        self.statusBar().showMessage("Preset acier inoxydable 316L chargé avec succès")
    
    def start_optimization(self):
        """Démarre l'optimisation dans un thread séparé."""
        try:
            # Construire le problème à partir de l'interface
            self.problem = self.build_problem_from_ui()
            
            # Valider le problème
            errors = self.problem.validate()
            if errors:
                QMessageBox.warning(self, "Erreurs de Validation", 
                                  "Erreurs détectées:\n" + "\n".join(errors))
                return
            
            # Démarrer l'optimisation
            self.optimization_thread = OptimizationThread(self.problem)
            self.optimization_thread.finished.connect(self.on_optimization_finished)
            self.optimization_thread.progress.connect(self.on_optimization_progress)
            self.optimization_thread.error.connect(self.on_optimization_error)
            
            # Mise à jour de l'interface
            self.solve_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # Mode indéterminé
            
            self.optimization_thread.start()
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du démarrage: {str(e)}")
    
    def stop_optimization(self):
        """Arrête l'optimisation en cours."""
        if self.optimization_thread and self.optimization_thread.isRunning():
            self.optimization_thread.terminate()
            self.optimization_thread.wait()
            
        self.solve_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.statusBar().showMessage("Optimisation arrêtée")
    
    def on_optimization_progress(self, message: str):
        """Gère les messages de progression."""
        self.statusBar().showMessage(message)
    
    def on_optimization_error(self, error_message: str):
        """Gère les erreurs d'optimisation."""
        QMessageBox.critical(self, "Erreur d'Optimisation", error_message)
        self.solve_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.statusBar().showMessage("Erreur d'optimisation")
    
    def on_optimization_finished(self, result: OptimizationResult):
        """Gère la fin de l'optimisation."""
        self.result = result
        self.solve_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setVisible(False)
        
        # Afficher les résultats
        self.display_results(result)
        
        # Passer à l'onglet des résultats
        self.tab_widget.setCurrentIndex(1)
        
        self.statusBar().showMessage(f"Optimisation terminée - Statut: {result.status}")
    
    def display_results(self, result: OptimizationResult):
        """Affiche les résultats de l'optimisation."""
        # Résumé
        self.status_label.setText(result.status)
        if result.objective_value is not None:
            self.objective_label.setText(f"{result.total_cost:.2f} €")
        else:
            self.objective_label.setText("N/A")
        
        self.solve_time_label.setText(f"{result.solve_time:.3f} s")
        self.total_weight_label.setText(f"{result.total_weight:.2f} kg")
        
        # Solution détaillée
        if result.solution:
            self.solution_table.setRowCount(len(result.solution))
            total_cost = sum(qty * mat.cost_per_kg for mat in self.problem.raw_materials 
                           for mat_name, qty in result.solution.items() if mat.name == mat_name)
            
            for i, (material_name, quantity) in enumerate(result.solution.items()):
                self.solution_table.setItem(i, 0, QTableWidgetItem(material_name))
                self.solution_table.setItem(i, 1, QTableWidgetItem(f"{quantity:.3f}"))
                
                # Trouver le coût
                material_cost = 0
                for mat in self.problem.raw_materials:
                    if mat.name == material_name:
                        material_cost = quantity * mat.cost_per_kg
                        break
                
                self.solution_table.setItem(i, 2, QTableWidgetItem(f"{material_cost:.2f}"))
                
                percentage = (quantity / result.total_weight * 100) if result.total_weight > 0 else 0
                self.solution_table.setItem(i, 3, QTableWidgetItem(f"{percentage:.2f}%"))
        
        # Composition finale
        if result.element_percentages:
            elements = list(result.element_percentages.keys())
            self.composition_table.setRowCount(len(elements))
            
            for i, element_symbol in enumerate(elements):
                percentage = result.element_percentages[element_symbol]
                self.composition_table.setItem(i, 0, QTableWidgetItem(element_symbol))
                self.composition_table.setItem(i, 1, QTableWidgetItem(f"{percentage:.3f}"))
                
                # Trouver les contraintes
                min_req = max_auth = "N/A"
                for element in self.problem.alloy_spec.elements:
                    if element.symbol == element_symbol:
                        min_req = f"{element.min_percent:.2f}"
                        max_auth = f"{element.max_percent:.2f}"
                        break
                
                self.composition_table.setItem(i, 2, QTableWidgetItem(min_req))
                self.composition_table.setItem(i, 3, QTableWidgetItem(max_auth))
    
    def update_visualization(self):
        """Met à jour les graphiques de visualisation."""
        if not self.result:
            return
            
        self.figure.clear()
        viz_type = self.viz_type_combo.currentText()
        
        if viz_type == "Répartition des Matières Premières":
            self.plot_material_distribution()
        elif viz_type == "Composition Chimique":
            self.plot_chemical_composition()
        elif viz_type == "Analyse des Contraintes":
            self.plot_constraints_analysis()
        elif viz_type == "Coûts par Composant":
            self.plot_cost_breakdown()
        
        self.canvas.draw()
    
    def plot_material_distribution(self):
        """Graphique en camembert de la répartition des matières premières."""
        if not self.result or not self.result.solution:
            return
            
        ax = self.figure.add_subplot(111)
        
        materials = list(self.result.solution.keys())
        quantities = list(self.result.solution.values())
        
        # Filtrer les quantités nulles
        non_zero_data = [(mat, qty) for mat, qty in zip(materials, quantities) if qty > 0.001]
        
        if non_zero_data:
            materials, quantities = zip(*non_zero_data)
            ax.pie(quantities, labels=materials, autopct='%1.1f%%', startangle=90)
            ax.set_title("Répartition des Matières Premières (en poids)")
    
    def plot_chemical_composition(self):
        """Graphique en barres de la composition chimique."""
        if not self.result or not self.result.element_percentages:
            return
            
        ax = self.figure.add_subplot(111)
        
        elements = list(self.result.element_percentages.keys())
        percentages = list(self.result.element_percentages.values())
        
        bars = ax.bar(elements, percentages, color='steelblue', alpha=0.7)
        
        # Ajouter les limites min/max si disponibles
        for i, element_symbol in enumerate(elements):
            for element in self.problem.alloy_spec.elements:
                if element.symbol == element_symbol:
                    ax.axhline(y=element.min_percent, color='red', linestyle='--', alpha=0.5)
                    ax.axhline(y=element.max_percent, color='red', linestyle='--', alpha=0.5)
                    break
        
        ax.set_ylabel('Pourcentage (%)')
        ax.set_title('Composition Chimique de l\'Alliage')
        ax.tick_params(axis='x', rotation=45)
    
    def plot_constraints_analysis(self):
        """Analyse de la satisfaction des contraintes."""
        if not self.result or not self.result.element_percentages:
            return
            
        ax = self.figure.add_subplot(111)
        
        # Préparer les données
        elements = []
        actual_values = []
        min_constraints = []
        max_constraints = []
        
        for element in self.problem.alloy_spec.elements:
            if element.symbol in self.result.element_percentages:
                elements.append(element.symbol)
                actual_values.append(self.result.element_percentages[element.symbol])
                min_constraints.append(element.min_percent)
                max_constraints.append(element.max_percent)
        
        x = range(len(elements))
        width = 0.25
        
        ax.bar([i - width for i in x], min_constraints, width, label='Min Requis', color='red', alpha=0.6)
        ax.bar(x, actual_values, width, label='Valeur Actuelle', color='green', alpha=0.8)
        ax.bar([i + width for i in x], max_constraints, width, label='Max Autorisé', color='red', alpha=0.6)
        
        ax.set_xlabel('Éléments')
        ax.set_ylabel('Pourcentage (%)')
        ax.set_title('Analyse des Contraintes de Composition')
        ax.set_xticks(x)
        ax.set_xticklabels(elements)
        ax.legend()
    
    def plot_cost_breakdown(self):
        """Répartition des coûts par matière première."""
        if not self.result or not self.result.solution:
            return
            
        ax = self.figure.add_subplot(111)
        
        materials = []
        costs = []
        
        for material_name, quantity in self.result.solution.items():
            if quantity > 0.001:
                for mat in self.problem.raw_materials:
                    if mat.name == material_name:
                        materials.append(material_name)
                        costs.append(quantity * mat.cost_per_kg)
                        break
        
        if materials and costs:
            ax.pie(costs, labels=materials, autopct='%1.1f%%', startangle=90)
            ax.set_title(f"Répartition des Coûts (Total: {sum(costs):.2f} €)")
    
    def build_problem_from_ui(self) -> BlendingProblem:
        """Construit un objet BlendingProblem à partir de l'interface."""
        # Récupérer les matières premières
        materials = self.materials_table.get_materials()
        
        if not materials:
            raise ValueError("Aucune matière première valide définie")
        
        # Récupérer les éléments
        elements = self.element_spec_widget.get_elements()
        
        if not elements:
            raise ValueError("Aucun élément de spécification défini")
        
        # Créer la spécification d'alliage
        alloy_spec = AlloySpecification(
            name=self.alloy_name_edit.text(),
            target_weight=self.target_weight_spin.value(),
            elements=elements,
            max_impurities=self.max_impurities_spin.value()
        )
        
        # Créer le problème
        problem = BlendingProblem(
            name=self.problem_name_edit.text(),
            raw_materials=materials,
            alloy_spec=alloy_spec
        )
        
        return problem
    
    def save_problem(self):
        """Sauvegarde le problème actuel."""
        try:
            problem = self.build_problem_from_ui()
            
            filename, _ = QFileDialog.getSaveFileName(
                self, "Sauvegarder le Problème", "", "Fichiers JSON (*.json)")
            
            if filename:
                problem.save_to_json(filename)
                self.statusBar().showMessage(f"Problème sauvegardé: {filename}")
                
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la sauvegarde: {str(e)}")
    
    def load_problem(self):
        """Charge un problème depuis un fichier."""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Charger un Problème", "", "Fichiers JSON (*.json)")
        
        if filename:
            try:
                self.problem = BlendingProblem.load_from_json(filename)
                self.load_problem_to_ui(self.problem)
                self.statusBar().showMessage(f"Problème chargé: {filename}")
                
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement: {str(e)}")
    
    def load_problem_to_ui(self, problem: BlendingProblem):
        """Charge un problème dans l'interface."""
        # Configuration générale
        self.problem_name_edit.setText(problem.name)
        self.alloy_name_edit.setText(problem.alloy_spec.name)
        self.target_weight_spin.setValue(problem.alloy_spec.target_weight)
        self.max_impurities_spin.setValue(problem.alloy_spec.max_impurities)
        
        # Matières premières
        self.materials_table.setRowCount(len(problem.raw_materials))
        for i, material in enumerate(problem.raw_materials):
            self.materials_table.setItem(i, 0, QTableWidgetItem(material.name))
            self.materials_table.setItem(i, 1, QTableWidgetItem(str(material.cost_per_kg)))
            self.materials_table.setItem(i, 2, QTableWidgetItem(str(material.availability)))
            self.materials_table.setItem(i, 3, QTableWidgetItem(str(material.density)))
            self.materials_table.setItem(i, 4, QTableWidgetItem(str(material.purity)))
            self.materials_table.setItem(i, 5, QTableWidgetItem(json.dumps(material.composition)))
        
        # TODO: Charger aussi les spécifications d'éléments


def main():
    """Point d'entrée principal de l'application."""
    app = QApplication(sys.argv)
    
    # Configuration de l'application
    app.setApplicationName("Optimisation de Mélange d'Alliages")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("INSAT - Recherche Opérationnelle")
    
    # Création et affichage de la fenêtre principale
    window = AlloyMainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()