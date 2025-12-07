# Architecture Technique et Documentation du Code

## Vue d'Ensemble de l'Architecture

L'application suit une architecture modulaire en couches, séparant clairement la logique métier, l'interface utilisateur et la gestion des données.

```
metallurgy_blending/
├── src/
│   ├── main.py              # Point d'entrée principal
│   ├── models/              # Modèles de données et optimisation
│   │   ├── data_model.py    # Classes de données métier
│   │   └── optimization_model.py  # Modèle d'optimisation Gurobi
│   ├── ui/                  # Interface utilisateur PyQt5
│   │   └── main_window.py   # Fenêtre principale et widgets
│   └── utils/               # Utilitaires et helpers
│       └── data_utils.py    # Validation et formatage des données
├── data/                    # Cas de test et exemples
├── docs/                    # Documentation
└── requirements.txt         # Dépendances Python
```

## Couche Modèle (src/models/)

### data_model.py

#### Classes Principales

**`Element`** - Représentation d'un élément chimique
```python
@dataclass
class Element:
    symbol: str              # Symbole chimique (Fe, Ni, etc.)
    name: str               # Nom complet
    min_percent: float      # Pourcentage minimum requis
    max_percent: float      # Pourcentage maximum autorisé
    target_percent: Optional[float]  # Cible exacte (optionnel)
```

**`RawMaterial`** - Matière première disponible
```python
@dataclass
class RawMaterial:
    name: str                    # Nom commercial
    cost_per_kg: float          # Coût unitaire (€/kg)
    availability: float         # Quantité disponible (kg)
    composition: Dict[str, float]  # Composition chimique
    density: float = 7.8        # Densité (g/cm³)
    purity: float = 100.0       # Pureté (%)
```

**`AlloySpecification`** - Spécifications de l'alliage cible
```python
@dataclass
class AlloySpecification:
    name: str                   # Nom de l'alliage
    target_weight: float        # Poids à produire (kg)
    elements: List[Element]     # Contraintes sur les éléments
    max_impurities: float = 2.0 # Impuretés maximales (%)
    # Propriétés physiques optionnelles
    min_hardness: Optional[float] = None
    max_hardness: Optional[float] = None
    melting_point_min: Optional[float] = None
    melting_point_max: Optional[float] = None
```

**`BlendingProblem`** - Problème complet de mélange
```python
@dataclass
class BlendingProblem:
    name: str
    raw_materials: List[RawMaterial]
    alloy_spec: AlloySpecification
    additional_constraints: Dict = field(default_factory=dict)
    
    def validate(self) -> List[str]:          # Validation des données
    def save_to_json(self, filepath: str):    # Sérialisation
    def load_from_json(cls, filepath: str):   # Désérialisation
```

### optimization_model.py

#### Modèle d'Optimisation

**`BlendingOptimizer`** - Solveur principal
```python
class BlendingOptimizer:
    def __init__(self, problem: BlendingProblem)
    def build_model(self) -> gp.Model        # Construction du modèle Gurobi
    def solve(self) -> OptimizationResult    # Résolution
    def _add_element_constraints(self, element: Element)  # Contraintes chimiques
    def _add_additional_constraints(self)    # Contraintes avancées
    def perform_sensitivity_analysis(self) -> Dict  # Analyse post-optimale
```

**Formulation Mathématique Implémentée :**
```python
# Variables de décision
for material in raw_materials:
    x[material.name] = model.addVar(
        lb=0,                        # Non-négativité
        ub=material.availability,    # Contrainte de disponibilité
        name=f"x_{material.name}"
    )

# Fonction objectif
objective = gp.quicksum(
    material.cost_per_kg * x[material.name] 
    for material in raw_materials
)
model.setObjective(objective, GRB.MINIMIZE)

# Contrainte de poids total
model.addConstr(
    gp.quicksum(x[material.name] for material in raw_materials) 
    == target_weight
)

# Contraintes de composition
for element in elements:
    element_content = gp.quicksum(
        material.get_element_content(element.symbol) / 100.0 * x[material.name]
        for material in raw_materials
    )
    
    # Contraintes min/max
    model.addConstr(element_content >= element.min_percent / 100.0 * target_weight)
    model.addConstr(element_content <= element.max_percent / 100.0 * target_weight)
```

**`OptimizationResult`** - Résultats de l'optimisation
```python
@dataclass
class OptimizationResult:
    status: str                          # OPTIMAL, INFEASIBLE, etc.
    objective_value: Optional[float]     # Valeur optimale
    solution: Dict[str, float]          # Solution {matière: quantité}
    element_percentages: Dict[str, float]  # Composition finale
    solve_time: float                   # Temps de résolution
    total_weight: float                 # Poids total
    total_cost: float                   # Coût total
    constraints_satisfied: Dict[str, bool]  # État des contraintes
    sensitivity_analysis: Optional[Dict] = None
```

## Couche Interface (src/ui/)

### main_window.py

#### Architecture de l'Interface

L'interface utilise le patron **Model-View-Controller** avec PyQt5 :

**`AlloyMainWindow`** - Fenêtre principale (Controller + View)
```python
class AlloyMainWindow(QMainWindow):
    def __init__(self):
        self.problem = None              # Modèle de données
        self.optimization_thread = None  # Thread de calcul
        self.result = None              # Résultats actuels
        
    # Méthodes de l'interface
    def setup_ui(self)                  # Construction de l'UI
    def create_problem_tab(self)        # Onglet configuration
    def create_results_tab(self)        # Onglet résultats
    def create_visualization_tab(self)   # Onglet graphiques
    
    # Méthodes de contrôle
    def start_optimization(self)        # Lancement optimisation
    def build_problem_from_ui(self) -> BlendingProblem  # UI → Modèle
    def display_results(self, result)   # Affichage résultats
```

#### Widgets Personnalisés

**`MaterialTableWidget`** - Table des matières premières
```python
class MaterialTableWidget(QTableWidget):
    def setup_table(self)               # Configuration colonnes/en-têtes
    def add_material_row(self, row: int)  # Ajout ligne
    def get_materials(self) -> List[RawMaterial]  # Extraction données
```

**`ElementSpecWidget`** - Spécification des éléments
```python
class ElementSpecWidget(QWidget):
    def setup_ui(self)                  # Table des éléments + contrôles
    def get_elements(self) -> List[Element]  # Extraction éléments actifs
```

#### Threading et Non-blocage

**`OptimizationThread`** - Thread d'optimisation
```python
class OptimizationThread(QThread):
    # Signaux PyQt pour communication inter-thread
    finished = pyqtSignal(OptimizationResult)
    progress = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def run(self):
        # Exécution de l'optimisation dans le thread séparé
        optimizer = BlendingOptimizer(self.problem)
        result = optimizer.solve()
        self.finished.emit(result)
```

**Avantages :**
- Interface reste réactive pendant l'optimisation
- Possibilité d'annuler les calculs longs
- Messages de progression en temps réel
- Gestion propre des erreurs

#### Visualisation avec Matplotlib

**Graphiques Intégrés :**
```python
# Canvas matplotlib intégré dans PyQt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

def create_visualization_tab(self):
    self.figure = Figure(figsize=(12, 8))
    self.canvas = FigureCanvasQTAgg(self.figure)
    
def plot_material_distribution(self):
    ax = self.figure.add_subplot(111)
    ax.pie(quantities, labels=materials, autopct='%1.1f%%')
    
def plot_chemical_composition(self):
    ax = self.figure.add_subplot(111)
    ax.bar(elements, percentages, color='steelblue')
    # Ajouter lignes min/max
    ax.axhline(y=element.min_percent, color='red', linestyle='--')
```

## Couche Utilitaires (src/utils/)

### data_utils.py

#### Validation Avancée
```python
class DataValidator:
    @staticmethod
    def validate_material_data(materials: List[Dict]) -> Tuple[bool, List[str]]
    @staticmethod  
    def validate_alloy_specification(alloy_spec: Dict) -> Tuple[bool, List[str]]

def validate_composition(composition: Dict[str, float]) -> Tuple[bool, List[str]]:
    # Vérification pourcentages positifs
    # Vérification somme ≤ 100%
    # Détection incohérences
```

#### Calculs de Propriétés
```python
def calculate_alloy_properties(composition: Dict[str, float]) -> Dict[str, float]:
    # Densité moyenne pondérée
    density = sum(mass_fraction / element_densities[elem] for elem, frac...)
    
    # Estimation dureté (formule empirique pour aciers)
    hardness = fe_content * 0.3 + cr_content * 1.2 + ni_content * 0.8 + c_content * 50
    
    # Point de fusion moyen pondéré
    melting_point = sum(melting_points[elem] * weight for elem, weight...)
```

#### Export et Formatage
```python
def export_results_to_csv(result_data: Dict, filename: str)
def format_currency(amount: float, currency="€") -> str
def format_percentage(value: float, decimals=2) -> str  
def format_weight(weight: float, unit="kg") -> str
```

## Flux de Données

### 1. Saisie Utilisateur
```
Interface PyQt → MaterialTableWidget.get_materials() 
               → ElementSpecWidget.get_elements()
               → AlloyMainWindow.build_problem_from_ui()
               → BlendingProblem
```

### 2. Validation
```
BlendingProblem → validate() 
                → DataValidator.validate_material_data()
                → DataValidator.validate_alloy_specification()
                → List[errors] ou validation OK
```

### 3. Optimisation
```
BlendingProblem → OptimizationThread.run()
                → BlendingOptimizer.build_model()
                → BlendingOptimizer.solve()
                → Gurobi resolution
                → OptimizationResult
```

### 4. Affichage
```
OptimizationResult → AlloyMainWindow.display_results()
                   → Update des tables et labels
                   → matplotlib graphiques
                   → Interface mise à jour
```

## Gestion des Erreurs

### Hiérarchie des Exceptions
```python
# Erreurs de données
class DataValidationError(Exception): pass
class CompositionError(DataValidationError): pass
class ConstraintError(DataValidationError): pass

# Erreurs d'optimisation  
class OptimizationError(Exception): pass
class InfeasibleProblemError(OptimizationError): pass
class UnboundedProblemError(OptimizationError): pass

# Erreurs d'interface
class UIError(Exception): pass
class FileFormatError(UIError): pass
```

### Gestion dans l'Interface
```python
def start_optimization(self):
    try:
        problem = self.build_problem_from_ui()
        errors = problem.validate()
        if errors:
            QMessageBox.warning(self, "Erreurs", "\n".join(errors))
            return
        # Lancer optimisation...
    except Exception as e:
        QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")
        logging.exception("Erreur lors de l'optimisation")
```

## Tests et Validation

### Tests Unitaires (Structure Suggérée)
```python
# tests/test_models.py
def test_element_creation()
def test_raw_material_composition()
def test_blending_problem_validation()
def test_optimization_steel_316L()

# tests/test_utils.py  
def test_composition_validation()
def test_alloy_properties_calculation()
def test_data_export()

# tests/test_integration.py
def test_full_workflow_steel()
def test_infeasible_problem_handling()
def test_ui_data_consistency()
```

### Tests de Performance
```python
# Benchmarks avec différentes tailles de problèmes
def benchmark_small_problem():   # < 10 matières premières
def benchmark_medium_problem():  # 10-50 matières premières  
def benchmark_large_problem():   # > 50 matières premières
```

## Extensibilité

### Ajout de Nouveaux Widgets
```python
# 1. Créer le widget
class NewConstraintWidget(QWidget):
    def get_constraints(self) -> List[Constraint]:
        pass

# 2. L'intégrer dans l'interface principale
def create_problem_tab(self):
    # ... code existant ...
    self.new_constraint_widget = NewConstraintWidget()
    layout.addWidget(self.new_constraint_widget)

# 3. Utiliser dans la construction du problème  
def build_problem_from_ui(self):
    constraints = self.new_constraint_widget.get_constraints()
    problem.additional_constraints.update(constraints)
```

### Ajout de Nouvelles Contraintes
```python
# Dans optimization_model.py
def _add_additional_constraints(self):
    # ... contraintes existantes ...
    
    # Nouvelle contrainte d'exemple
    if 'environmental' in self.problem.additional_constraints:
        co2_limit = self.problem.additional_constraints['environmental']['co2_max']
        co2_emission = gp.quicksum(
            material.co2_footprint * self.variables[material.name]
            for material in self.problem.raw_materials
        )
        self.model.addConstr(co2_emission <= co2_limit, name="co2_limit")
```

### Ajout de Nouvelles Visualisations
```python
# Dans main_window.py
def update_visualization(self):
    viz_type = self.viz_type_combo.currentText()
    
    # ... cases existants ...
    elif viz_type == "Nouvelle Visualisation":
        self.plot_new_visualization()

def plot_new_visualization(self):
    ax = self.figure.add_subplot(111)
    # Code du nouveau graphique...
    ax.set_title("Nouveau Type de Graphique")
```

## Bonnes Pratiques

### Code Quality
- **Type Hints** : Utilisation systématique pour la documentation du code
- **Docstrings** : Documentation des classes et méthodes principales
- **Dataclasses** : Simplification des modèles de données
- **Error Handling** : Gestion appropriée des exceptions

### Performance
- **Lazy Loading** : Chargement des données à la demande
- **Caching** : Mise en cache des résultats d'optimisation
- **Threading** : Calculs longs dans des threads séparés
- **Memory Management** : Nettoyage des gros objets Gurobi

### Maintenabilité
- **Separation of Concerns** : Séparation claire des responsabilités
- **Single Responsibility** : Une classe = une responsabilité
- **Configuration** : Paramètres externalisables  
- **Logging** : Traçabilité des opérations importantes

Cette architecture modulaire permet une maintenance facile et des extensions futures de l'application.