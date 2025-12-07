# Guide d'Installation et d'Utilisation

## Prérequis Système

### Logiciels Requis
- **Python 3.8+** (recommandé : Python 3.9 ou 3.10)
- **Gurobi Optimizer 10.0+** avec licence valide
- **Système d'exploitation** : Windows 10+, macOS 10.15+, ou Linux Ubuntu 18.04+

### Vérification Python
```bash
python --version
# ou
python3 --version
```

## Installation

### 1. Cloner ou Télécharger le Projet
```bash
# Si vous avez Git
git clone <repository_url>
cd metallurgy_blending

# Ou télécharger et extraire l'archive ZIP
```

### 2. Créer un Environnement Virtuel (Recommandé)
```bash
# Créer l'environnement virtuel
python -m venv venv

# Activer l'environnement (Windows)
venv\Scripts\activate

# Activer l'environnement (macOS/Linux)
source venv/bin/activate
```

### 2. Installer les Dépendances

#### Sur les Environnements Python Gérés (Kali Linux, etc.)
```bash
# Utiliser le script d'installation automatique
./install.sh

# Ou manuellement créer un environnement virtuel
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Sur les Systèmes Standards
```bash
# Installer directement (si autorisé)
pip install -r requirements.txt

# Ou avec un environnement virtuel (recommandé)
python -m venv venv
# Windows: venv\Scripts\activate  
# Linux/macOS: source venv/bin/activate
pip install -r requirements.txt
```

### 4. Configuration de Gurobi (Optionnel)

⚠️ **Note Importante**: L'application fonctionne en **mode simulation** sans Gurobi, avec des résultats fictifs pour tester l'interface.

#### Option A : Mode Simulation (Recommandé pour les Tests)
- ✅ **Aucune configuration requise**
- ✅ **Interface complètement fonctionnelle**
- ✅ **Résultats de démonstration**
- ⚠️ **Optimisation simulée** (pas de vraie résolution)

#### Option B : Licence Académique Gurobi (Pour la Résolution Réelle)
1. Créer un compte sur [Gurobi.com](https://www.gurobi.com)
2. Télécharger la licence académique gratuite
3. Installer Gurobi :
   ```bash
   # Dans votre environnement virtuel
   source venv/bin/activate  # Linux/macOS
   # ou venv\Scripts\activate  # Windows
   pip install gurobipy
   ```
4. Suivre les instructions d'installation de Gurobi

#### Option C : Licence Commerciale
1. Obtenir une licence commerciale de Gurobi
2. Configurer la variable d'environnement `GRB_LICENSE_FILE`

#### Vérification de l'Installation Gurobi
```python
# Test rapide dans Python
import gurobipy as gp
print("Gurobi installé avec succès!")
```

## Lancement de l'Application

### Méthode Standard
```bash
# Depuis le répertoire racine du projet
cd src
python main.py
```

### Méthode Alternative
```bash
# Depuis le répertoire racine
python -m src.main
```

### Sous Windows (Double-clic)
Créer un fichier `launch.bat` :
```batch
@echo off
cd /d "%~dp0"
cd src
python main.py
pause
```

## Guide d'Utilisation

### 1. Interface Principale

L'application s'ouvre avec trois onglets principaux :

#### 🔧 Configuration
- **Configuration générale** : Nom du problème, type d'alliage, poids cible
- **Spécifications des éléments** : Définition des contraintes chimiques
- **Matières premières** : Données des matériaux disponibles

#### 📊 Résultats  
- **Résumé de l'optimisation** : Statut, coût, temps de résolution
- **Solution détaillée** : Quantités optimales par matière première
- **Composition finale** : Pourcentages des éléments chimiques

#### 📈 Visualisation
- **Répartition des matières premières** : Graphique en camembert
- **Composition chimique** : Graphique en barres avec limites
- **Analyse des contraintes** : Comparaison min/max/actuel
- **Coûts par composant** : Répartition financière

### 2. Workflow Typique

#### Étape 1 : Configuration du Problème
1. **Nommer le projet** dans "Configuration Générale"
2. **Définir l'alliage cible** (nom, poids, impuretés max)
3. **Activer les éléments** dans "Spécifications des Éléments"
4. **Ajuster les contraintes** (min%, max%, cible%)

#### Étape 2 : Saisie des Matières Premières
1. **Ajouter des lignes** avec le bouton "Ajouter Matière Première"
2. **Remplir les données** :
   - Nom de la matière première
   - Coût par kg (€)
   - Disponibilité (kg)
   - Densité (g/cm³)
   - Pureté (%)
   - Composition chimique (format JSON)

**Exemple de composition JSON :**
```json
{"Fe": 65.0, "Cr": 17.0, "Ni": 12.0, "Mo": 2.5, "C": 0.03}
```

#### Étape 3 : Utilisation des Presets
- **Bouton "Charger Preset Acier"** : Charge automatiquement un exemple d'acier inoxydable
- **Menu "📂 Charger"** : Importer un cas de test depuis le dossier `data/`

#### Étape 4 : Optimisation
1. **Cliquer sur "🚀 Optimiser"** dans la barre d'outils
2. **Observer la progression** dans la barre de statut
3. **Attendre les résultats** (quelques secondes)

#### Étape 5 : Analyse des Résultats
1. **Consulter l'onglet Résultats** pour les données détaillées
2. **Utiliser l'onglet Visualisation** pour les graphiques
3. **Exporter les résultats** si nécessaire

### 3. Gestion des Fichiers

#### Sauvegarde
- **Menu "💾 Sauvegarder"** : Exporter la configuration au format JSON
- **Nom suggéré** : `projet_alliage_AAAA-MM-JJ.json`

#### Chargement
- **Menu "📂 Charger"** : Importer une configuration existante
- **Formats supportés** : Fichiers JSON (.json)

### 4. Cas de Test Fournis

Le dossier `data/` contient quatre cas de test prêts à utiliser :

1. **steel_316L_medical.json** - Acier inoxydable grade médical
2. **aluminum_7075_aerospace.json** - Alliage aluminium aéronautique  
3. **tool_steel_m2.json** - Acier à outils haute vitesse
4. **inconel_718_turbine.json** - Superalliage pour turbomachines

### 5. Interprétation des Résultats

#### Statuts Possibles
- **OPTIMAL** : Solution optimale trouvée
- **INFAISABLE** : Aucune solution ne satisfait toutes les contraintes
- **NON_BORNE** : Problème de modélisation (coûts négatifs)
- **ERREUR** : Problème technique (vérifier Gurobi)

#### Indicateurs de Qualité
- **Temps de résolution** : < 10s pour la plupart des cas
- **Contraintes satisfaites** : Toutes doivent être "✓"
- **Coût total** : Cohérent avec les prix du marché

#### Analyse Avancée
- **Prix duaux** : Coût marginal de modification des contraintes
- **Coûts réduits** : Écart au coût d'entrée dans la solution
- **Analyse de sensibilité** : Robustesse de la solution

## Dépannage

### Problèmes Courants

#### Erreur "Gurobi not found"
```bash
# Vérifier l'installation
pip show gurobipy

# Réinstaller si nécessaire  
pip uninstall gurobipy
pip install gurobipy
```

#### Erreur "No license found"
1. Vérifier la variable d'environnement `GRB_LICENSE_FILE`
2. Renouveler la licence académique si expirée
3. Contacter l'administrateur pour les licences commerciales

#### Interface ne s'ouvre pas
```bash
# Vérifier PyQt5
python -c "import PyQt5; print('PyQt5 OK')"

# Alternative : utiliser PySide2
pip uninstall PyQt5
pip install PySide2
# Modifier les imports dans le code : PyQt5 → PySide2
```

#### Erreurs de données
- **Composition > 100%** : Vérifier les pourcentages dans les matières premières
- **Contraintes contradictoires** : Relaxer les bornes min/max des éléments
- **Disponibilités insuffisantes** : Augmenter les quantités disponibles

### Logs et Débogage

#### Activer les logs Gurobi
```python
# Dans optimization_model.py, modifier :
self.model.setParam('OutputFlag', 1)  # Au lieu de 0
```

#### Mode debug Python
```bash
python -u src/main.py
```

### Support et Contact

- **Documentation technique** : Consulter `docs/`
- **Problèmes GitHub** : Créer une issue avec logs d'erreur
- **Formation Gurobi** : [gurobi.com/resources](https://www.gurobi.com/resources/)

## Performances et Limites

### Configurations Recommandées
- **Petits problèmes** (< 10 matières premières) : 4GB RAM, processeur standard
- **Problèmes moyens** (10-50 matières premières) : 8GB RAM, processeur récent
- **Gros problèmes** (> 50 matières premières) : 16GB+ RAM, processeur multicœur

### Limites Actuelles
- **Matières premières** : Pas de limite théorique (testé jusqu'à 100)
- **Éléments chimiques** : Pas de limite (testé jusqu'à 20)
- **Contraintes additionnelles** : Extension possible du modèle
- **Interface** : Optimisée pour écrans 1920x1080+

### Optimisations Futures
- Mise en cache des résolutions
- Parallélisation pour les analyses de sensibilité
- Support des problèmes multi-objectifs
- Interface web pour l'accès distant