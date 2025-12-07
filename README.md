# Operations Research Project Collection

This repository contains a collection of Operations Research (RO) projects developed by our group. A unified launcher is provided to execute and evaluate each student's contribution from a single interface.

## 🚀 Quick Start

1.  **Activate the Environment**:
    ```bash
    source venv/bin/activate
    ```

2.  **Run the Unified Launcher**:
    ```bash
    python launcher.py
    ```

3.  **Select a Project**:
    Click on any student's name to launch their respective application.

## 📂 Project List

| Student Name | Project Description |
| :--- | :--- |
| **Ahmed Saad** | **Student Assignment Optimization**: A PLNE model to assign students to projects maximizing preference satisfaction under capacity and incompatibility constraints. |
| **Ahmed Ben Rejeb** | **Optimization Project**: Implementation of RO problem 16.3. |
| **Seifeddine Koubaa** | **Transport Optimization**: Application for multi-modal transport flow optimization. |
| **Abdelkader Ammar** | **Graph Flow Optimization**: Resolution of Graph/Flow Problem 17. |
| **Amine Jebari** | **Optimization Problem 15**: Implementation and resolution of Problem 15. |

## 🛠️ Technical Details

-   **Language**: Python 3
-   **GUI Frameworks**: PySide6, PyQt6, PyQt5 (All integrated)
-   **Solvers**: Gurobi, Custom Algorithms
-   **Dependencies**: All necessary libraries are pre-installed in the provided virtual environment (`venv`).

## ⚠️ Note on Execution

Ensure that a valid Gurobi license is available for projects utilizing the Gurobi solver. For testing purposes, some projects (like Ahmed Saad's) include a "Mock Solver" mode that runs without a license.
