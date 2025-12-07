#!/usr/bin/env python3
"""
Launcher simplifié pour l'application de mélange d'alliages.
Ce script évite les problèmes d'imports relatifs.
"""

import sys
import os
from pathlib import Path

# Configuration des chemins
project_root = Path(__file__).parent
src_dir = project_root / "src"
sys.path.insert(0, str(src_dir))

# Vérification de l'environnement virtuel
venv_dir = project_root / "venv"
if venv_dir.exists():
    print("🔧 Environnement virtuel détecté")
    
# Configuration de Gurobi si disponible
gurobi_license = "/run/media/ahmed/BEBC72DFBC72919F/RT3/RO/RO_16/gurobi.lic"
if os.path.exists(gurobi_license):
    os.environ["GRB_LICENSE_FILE"] = gurobi_license
    print("🔑 Licence Gurobi configurée")

# Importer et lancer l'application
try:
    print("🚀 Lancement de l'application de mélange d'alliages...")
    
    # Import direct des modules
    sys.path.insert(0, str(src_dir / "ui"))
    sys.path.insert(0, str(src_dir / "models")) 
    sys.path.insert(0, str(src_dir / "utils"))
    
    from main_window import main
    main()
    
except ImportError as e:
    print(f"❌ Erreur d'import: {e}")
    print("💡 Vérifier que toutes les dépendances sont installées")
    sys.exit(1)
except Exception as e:
    print(f"❌ Erreur: {e}")
    sys.exit(1)