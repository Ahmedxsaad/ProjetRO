# Transport Optimization Application (Project RO)

## Overview
This application solves the Minimum Cost Flow problem for a multi-modal passenger transport network. It uses Gurobi for optimization and PyQt6 for the user interface.

## Prerequisites
1. Python 3.9+
2. Gurobi Optimizer (and license)

## Installation
1. Install dependencies:
   ```bash
   pip install -r TransportApp/requirements.txt
   ```

## Running the Application
To run the application with the Graphical User Interface:

```bash
python run.py
```

## Usage
1. **Hubs & Demand Tab:**
   - Add hubs (cities/locations).
   - Set Net Demand:
     - Positive value (e.g., 100) = Source (Supply)
     - Negative value (e.g., -100) = Sink (Demand)
     - Zero (0) = Transit Hub
   - Set Hub Capacity (max flow through the hub).

2. **Routes (Arcs) Tab:**
   - Define connections between hubs.
   - Select Mode (Train, Bus, Flight).
   - Set Cost per passenger and Link Capacity.

3. **Optimization Results Tab:**
   - Click "SOLVE OPTIMIZATION".
   - View optimal flows and the network visualization.

## Structure
- `TransportApp/model/`: Contains the Gurobi optimization logic.
- `TransportApp/ui/`: Contains the PyQt6 main window code.
- `run.py`: Entry point for the application.

