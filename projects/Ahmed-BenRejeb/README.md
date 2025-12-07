# 🏭 Metallurgy Alloy Blending Optimizer

Une application d'optimisation pour le mélange d'alliages métallurgiques utilisant la programmation linéaire avec Gurobi.

## 📋 Description

Cette application résout des problèmes de mélange d'alliages en métallurgie en optimisant les proportions de matières premières pour atteindre une composition chimique cible tout en minimisant les coûts.

## ✨ Fonctionnalités

- **Interface graphique professionnelle** (PyQt5)
- **Optimisation avec Gurobi** (solveur industriel)
- **Visualisations interactives** (Matplotlib)
- **Cas de test industriels** inclus
- **Analyse de sensibilité** des résultats
- **Export/Import** de données JSON

## 🛠️ Installation

### Prérequis
- Python 3.8+
- Licence Gurobi (académique ou commerciale)

### 1. Cloner le projet
```bash
git clone <votre-repo>
cd metallurgy_blending
```

### 2. Créer un environnement virtuel
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

### 3. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 4. Configurer Gurobi
Placez votre fichier de licence `gurobi.lic` dans le répertoire du projet ou configurez la variable d'environnement :
```bash
export GRB_LICENSE_FILE=/path/to/your/gurobi.lic
```

## 🚀 Utilisation

### Lancement rapide
```bash
python run_app.py
```

### Interface principale

1. **Chargement des données** :
   - Cliquez sur "Charger Données" pour importer un cas de test
   - Ou créez votre propre problème manuellement

2. **Configuration du problème** :
   - **Matières premières** : Définissez composition et coût
   - **Spécifications** : Définissez les contraintes d'éléments chimiques
   - **Quantité cible** : Spécifiez la quantité d'alliage à produire

3. **Optimisation** :
   - Cliquez sur "Optimiser" pour résoudre le problème
   - Les résultats s'affichent automatiquement

4. **Visualisation** :
   - Graphiques de composition
   - Analyse des contraintes
   - Distribution des coûts

## 📊 Cas de test inclus

Le répertoire `data/` contient 4 cas industriels :

### 1. Acier 316L Médical (`steel_316L_medical.json`)
- **Application** : Implants médicaux
- **Contraintes** : Faible carbone, haute résistance à la corrosion
- **Matières** : Acier inox, ferrochrome, ferronickel

### 2. Alliage Aluminium 7075 (`aluminum_7075_aerospace.json`)
- **Application** : Aéronautique/spatial
- **Contraintes** : Haute résistance mécanique
- **Matières** : Aluminium pur, alliages Zn-Mg-Cu

### 3. Acier à Outils M2 (`tool_steel_m2.json`)
- **Application** : Outillage industriel
- **Contraintes** : Haute dureté, résistance à l'usure
- **Matières** : Acier base, tungstène, molybdène

### 4. Superalliage Inconel 718 (`inconel_718_turbine.json`)
- **Application** : Turbines à gaz
- **Contraintes** : Résistance haute température
- **Matières** : Nickel, chrome, fer, niobium

## 🔧 Structure du projet

```
metallurgy_blending/
├── src/
│   ├── models/
│   │   ├── data_model.py          # Modèles de données
│   │   └── optimization_model.py  # Optimisation Gurobi
│   ├── ui/
│   │   └── main_window.py         # Interface PyQt5
│   └── utils/
│       └── data_utils.py          # Utilitaires
├── data/                          # Cas de test
├── docs/                          # Documentation
├── requirements.txt               # Dépendances
├── run_app.py                     # Launcher principal
└── README.md                      # Ce fichier
```

## 🎯 Utilisation avancée

### Création d'un nouveau problème

1. **Définir les matières premières** :
```python
# Exemple : Acier au carbone
{
    "name": "Acier C45",
    "composition": {"C": 0.45, "Mn": 0.7, "Si": 0.25, "Fe": 98.6},
    "cost": 800,  # €/tonne
    "availability": 1000  # tonnes
}
```

2. **Spécifier l'alliage cible** :
```python
# Contraintes sur la composition finale
{
    "element": "C",
    "min_percentage": 0.40,
    "max_percentage": 0.50
}
```

### Export/Import de données

- **Exporter** : Bouton "Exporter Résultats" → fichier JSON
- **Importer** : Bouton "Charger Données" → sélectionner fichier JSON

## 📈 Interprétation des résultats

### Tableau des résultats
- **Quantité optimale** : Proportion de chaque matière première
- **Coût unitaire** : Coût par tonne d'alliage produit
- **Composition finale** : Pourcentages des éléments chimiques

### Graphiques
- **Composition par éléments** : Répartition des éléments chimiques
- **Coûts par matière** : Contribution au coût total
- **Contraintes actives** : Limites atteintes

## 🔍 Dépannage

### Erreur de licence Gurobi
```
GurobiError: No valid license found
```
**Solution** : Vérifier le chemin vers `gurobi.lic` ou configurer `GRB_LICENSE_FILE`

### Problème non réalisable
```
Status: INFEASIBLE
```
**Solution** : Vérifier que les contraintes ne sont pas contradictoires

### Interface qui ne se lance pas
```
ModuleNotFoundError: No module named 'PyQt5'
```
**Solution** : Réinstaller les dépendances avec `pip install -r requirements.txt`

## 📚 Ressources

- [Documentation Gurobi](https://www.gurobi.com/documentation/)
- [PyQt5 Documentation](https://doc.qt.io/qtforpython/)
- [Métallurgie et alliages](https://fr.wikipedia.org/wiki/Alliage)

## 📄 Licence

Projet académique - Utilisation non commerciale uniquement.

## 👨‍💻 Auteur

Développé pour le cours de Recherche Opérationnelle - Problème RO-16

---

**🎯 Prêt à optimiser vos alliages métallurgiques !**