"""
Demonstration Test - Shows the solver working with realistic data
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.model.data_models import Student, Project
from src.model.optimization_model import StudentAssignmentSolver
from src.model.mock_solver import MockSolver

def print_separator():
    print("\n" + "="*70 + "\n")

def demo_simple_scenario():
    print_separator()
    print("DEMO 1: Simple Assignment (3 Students, 2 Projects)")
    print_separator()
    
    # Create students with preferences
    students = [
        Student(1, "Alice", {101: 10, 102: 3}),
        Student(2, "Bob", {101: 5, 102: 8}),
        Student(3, "Charlie", {101: 7, 102: 9}),
    ]
    
    # Create projects with capacities
    projects = [
        Project(101, "Web Development", capacity_min=1, capacity_max=2),
        Project(102, "Mobile App", capacity_min=1, capacity_max=2),
    ]
    
    print("Students and Preferences:")
    for s in students:
        prefs = ", ".join([f"{p_id}:{score}" for p_id, score in s.preferences.items()])
        print(f"  {s.name} (ID {s.id}): {prefs}")
    
    print("\nProjects and Capacities:")
    for p in projects:
        print(f"  {p.name} (ID {p.id}): Min={p.capacity_min}, Max={p.capacity_max}")
    
    # Solve with Mock Solver
    print("\n[Running Mock Solver...]")
    solver = MockSolver()
    result = solver.solve(students, projects)
    
    print(f"\nResult: {result.status}")
    print(f"Objective Value: {result.objective_value}")
    print("\nAssignments:")
    for s_id, p_id in result.student_assignments.items():
        s_name = next((s.name for s in students if s.id == s_id), f"Student {s_id}")
        p_name = next((p.name for p in projects if p.id == p_id), f"Project {p_id}")
        student = next((s for s in students if s.id == s_id), None)
        score = student.preferences.get(p_id, 0) if student else 0
        print(f"  {s_name} → {p_name} (Satisfaction: {score})")

def demo_with_incompatibility():
    print_separator()
    print("DEMO 2: With Incompatibility Constraints (5 Students, 3 Projects)")
    print_separator()
    
    # Create students with preferences
    students = [
        Student(1, "Alice", {101: 10, 102: 7, 103: 5}, incompatible_with=[2]),
        Student(2, "Bob", {101: 9, 102: 6, 103: 4}, incompatible_with=[1]),
        Student(3, "Charlie", {101: 8, 102: 10, 103: 6}),
        Student(4, "Diana", {101: 6, 102: 8, 103: 10}, incompatible_with=[5]),
        Student(5, "Eve", {101: 7, 102: 5, 103: 9}, incompatible_with=[4]),
    ]
    
    # Create projects with capacities
    projects = [
        Project(101, "AI Research", capacity_min=1, capacity_max=2),
        Project(102, "Data Science", capacity_min=1, capacity_max=2),
        Project(103, "Cybersecurity", capacity_min=1, capacity_max=2),
    ]
    
    print("Students and Preferences:")
    for s in students:
        prefs = ", ".join([f"{p_id}:{score}" for p_id, score in s.preferences.items()])
        incomp = f" [Incompatible with: {', '.join(map(str, s.incompatible_with))}]" if s.incompatible_with else ""
        print(f"  {s.name} (ID {s.id}): {prefs}{incomp}")
    
    print("\nProjects and Capacities:")
    for p in projects:
        print(f"  {p.name} (ID {p.id}): Min={p.capacity_min}, Max={p.capacity_max}")
    
    # Solve with Mock Solver
    print("\n[Running Mock Solver...]")
    solver = MockSolver()
    result = solver.solve(students, projects)
    
    print(f"\nResult: {result.status}")
    print(f"Objective Value: {result.objective_value}")
    print("\nAssignments:")
    
    # Group by project
    project_assignments = {}
    for p in projects:
        project_assignments[p.id] = []
    
    for s_id, p_id in result.student_assignments.items():
        project_assignments[p_id].append(s_id)
    
    for p_id, student_ids in project_assignments.items():
        p_name = next((p.name for p in projects if p.id == p_id), f"Project {p_id}")
        print(f"\n  {p_name}:")
        if student_ids:
            for s_id in student_ids:
                s_name = next((s.name for s in students if s.id == s_id), f"Student {s_id}")
                student = next((s for s in students if s.id == s_id), None)
                score = student.preferences.get(p_id, 0) if student else 0
                print(f"    - {s_name} (Satisfaction: {score})")
        else:
            print(f"    - (Empty)")
    
    # Verify incompatibilities are respected
    print("\nVerifying Incompatibility Constraints:")
    violations = []
    for p_id, student_ids in project_assignments.items():
        for i, s1_id in enumerate(student_ids):
            for s2_id in student_ids[i+1:]:
                s1 = next((s for s in students if s.id == s1_id), None)
                if s1 and s2_id in s1.incompatible_with:
                    violations.append(f"  ❌ {s1.name} and Student {s2_id} are incompatible but both in Project {p_id}")
    
    if violations:
        print("\n".join(violations))
    else:
        print("  ✓ All incompatibility constraints are respected!")

def demo_gurobi_if_available():
    print_separator()
    print("DEMO 3: Testing Gurobi Solver (if available)")
    print_separator()
    
    students = [
        Student(1, "Alice", {101: 10, 102: 1}),
        Student(2, "Bob", {101: 1, 102: 10}),
    ]
    
    projects = [
        Project(101, "Project A", capacity_min=1, capacity_max=1),
        Project(102, "Project B", capacity_min=1, capacity_max=1),
    ]
    
    print("Students and Preferences:")
    for s in students:
        prefs = ", ".join([f"{p_id}:{score}" for p_id, score in s.preferences.items()])
        print(f"  {s.name} (ID {s.id}): {prefs}")
    
    print("\nProjects and Capacities:")
    for p in projects:
        print(f"  {p.name} (ID {p.id}): Min={p.capacity_min}, Max={p.capacity_max}")
    
    print("\n[Running Gurobi Solver...]")
    solver = StudentAssignmentSolver()
    result = solver.solve(students, projects)
    
    print(f"\nResult: {result.status}")
    
    if "ERROR" not in result.status:
        print(f"Objective Value: {result.objective_value}")
        print("\nAssignments:")
        for s_id, p_id in result.student_assignments.items():
            s_name = next((s.name for s in students if s.id == s_id), f"Student {s_id}")
            p_name = next((p.name for p in projects if p.id == p_id), f"Project {p_id}")
            student = next((s for s in students if s.id == s_id), None)
            score = student.preferences.get(p_id, 0) if student else 0
            print(f"  {s_name} → {p_name} (Satisfaction: {score})")
    else:
        print("Gurobi is not available. The GUI allows you to use Mock Solver for testing.")

if __name__ == "__main__":
    demo_simple_scenario()
    demo_with_incompatibility()
    demo_gurobi_if_available()
    
    print_separator()
    print("DEMONSTRATION COMPLETE")
    print("\nTo run the GUI application on a machine with a display:")
    print("  1. cd /home/fantazy/.gemini/antigravity/scratch/ro_project")
    print("  2. source venv/bin/activate")
    print("  3. python main.py")
    print_separator()
