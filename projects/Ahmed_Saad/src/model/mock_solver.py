from typing import List
from .data_models import Student, Project, AssignmentResult
import time

class MockSolver:
    def solve(self, students: List[Student], projects: List[Project], time_limit: int = 60) -> AssignmentResult:
        """
        A dumb greedy solver for testing UI flow.
        Does NOT guarantee optimality or constraint satisfaction.
        """
        time.sleep(1) # Simulate work
        
        assignments = {p.id: [] for p in projects}
        student_assignments = {}
        obj_val = 0.0
        
        # Simple greedy assignment
        # Sort students by ID for determinism
        for s in sorted(students, key=lambda x: x.id):
            # Try to assign to best available preference
            sorted_prefs = sorted(s.preferences.items(), key=lambda item: item[1], reverse=True)
            assigned = False
            for pid, score in sorted_prefs:
                # Find project
                proj = next((p for p in projects if p.id == pid), None)
                if proj and len(assignments[pid]) < proj.capacity_max:
                    assignments[pid].append(s.id)
                    student_assignments[s.id] = pid
                    obj_val += score
                    assigned = True
                    break
            
            # Fallback: assign to first available project with space
            if not assigned:
                for p in projects:
                    if len(assignments[p.id]) < p.capacity_max:
                        assignments[p.id].append(s.id)
                        student_assignments[s.id] = p.id
                        obj_val += 0 # No preference score
                        assigned = True
                        break
        
        # Check if all assigned (Mock doesn't handle infeasibility well, just returns what it has)
        if len(student_assignments) == len(students):
             return AssignmentResult(
                status="OPTIMAL (MOCK)",
                objective_value=obj_val,
                assignments=assignments,
                student_assignments=student_assignments,
                solve_time=1.0
            )
        else:
             return AssignmentResult(
                status="INFEASIBLE (MOCK)",
                objective_value=obj_val,
                assignments=assignments,
                student_assignments=student_assignments,
                solve_time=1.0
            )
