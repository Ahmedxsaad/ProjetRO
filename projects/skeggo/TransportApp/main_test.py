import sys
import os

# Add the project root to Python path to allow imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Create window
    window = MainWindow()
    
    # Pre-populate with Test Data (Problème 14 - Example)
    # Hubs: Paris (Supply 100), Lyon (Transit), Marseille (Demand 100)
    
    # Add Hubs
    # Simulate user input behavior or directly modify data structures
    # Direct modification for speed in this test script
    
    window.hub_name_input.setText("Paris")
    window.demand_input.setText("100")
    window.hub_cap_input.setText("500")
    window.add_hub()
    
    window.hub_name_input.setText("Marseille")
    window.demand_input.setText("-100")
    window.hub_cap_input.setText("500")
    window.add_hub()
    
    window.hub_name_input.setText("Lyon")
    window.demand_input.setText("0")
    window.hub_cap_input.setText("200")
    window.add_hub()
    
    # Add Arcs (Paris -> Lyon)
    window.origin_combo.setCurrentText("Paris")
    window.dest_combo.setCurrentText("Lyon")
    window.mode_combo.setCurrentText("Train")
    window.cost_input.setText("50")
    window.link_cap_input.setText("80")
    window.add_arc()
    
    window.mode_combo.setCurrentText("Bus")
    window.cost_input.setText("20")
    window.link_cap_input.setText("50")
    window.add_arc()
    
    # Add Arcs (Lyon -> Marseille)
    window.origin_combo.setCurrentText("Lyon")
    window.dest_combo.setCurrentText("Marseille")
    window.mode_combo.setCurrentText("Train")
    window.cost_input.setText("50")
    window.link_cap_input.setText("80")
    window.add_arc()
    
    window.mode_combo.setCurrentText("Bus")
    window.cost_input.setText("20")
    window.link_cap_input.setText("50")
    window.add_arc()

    # Add Direct Arc (Paris -> Marseille) - Expensive but fast?
    window.origin_combo.setCurrentText("Paris")
    window.dest_combo.setCurrentText("Marseille")
    window.mode_combo.setCurrentText("Flight")
    window.cost_input.setText("150")
    window.link_cap_input.setText("100")
    window.add_arc()
    
    print("Test data loaded. Launching GUI...")
    window.show()
    sys.exit(app.exec())

