"""
Point d'entrée principal de l'application de mélange d'alliages métallurgiques.

Ce module lance l'interface graphique PyQt5 et gère l'initialisation de l'application.
"""

import sys
import os

# Ajouter le répertoire parent au path pour les imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, current_dir)
sys.path.insert(0, parent_dir)

# Imports directs sans relative paths
if __name__ == "__main__":
    from ui.main_window import main
    main()