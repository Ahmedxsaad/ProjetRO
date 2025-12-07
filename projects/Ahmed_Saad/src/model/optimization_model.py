try:
    import gurobipy as gp
    from gurobipy import GRB
except ImportError:
    gp = None
    GRB = None
from typing import List, Dict, Tuple
from .data_models import Student, Project, AssignmentResult

class StudentAssignmentSolver:
    def __init__(self):
        self.model = None

    def solve(self, students: List[Student], projects: List[Project], time_limit: int = 60) -> AssignmentResult:
        """
        Solves the student assignment problem using Gurobi.
        """
        if gp is None:
            return AssignmentResult(
                status="ERROR: Gurobi not installed",
                objective_value=0.0,
                assignments={},
                student_assignments={},
                solve_time=0.0
            )

        try:
            # Create a new model
            m = gp.Model("student_assignment")
            m.setParam('TimeLimit', time_limit)
            m.setParam('OutputFlag', 0)  # Suppress console output

            # --- Decision Variables ---
            # x[i, j] = 1 if student i is assigned to project j
            x = {}
            for s in students:
                for p in projects:
                    x[s.id, p.id] = m.addVar(vtype=GRB.BINARY, name=f"x_{s.id}_{p.id}")

            # --- Objective Function ---
            # Maximize total preference score
            # If a student has no preference for a project, we assume score 0 (or a default low score)
            obj_expr = gp.LinExpr()
            for s in students:
                for p in projects:
                    score = s.preferences.get(p.id, 0)
                    obj_expr += score * x[s.id, p.id]
            
            m.setObjective(obj_expr, GRB.MAXIMIZE)

            # --- Constraints ---

            # 1. Each student assigned to exactly one project
            for s in students:
                m.addConstr(gp.quicksum(x[s.id, p.id] for p in projects) == 1, name=f"assign_{s.id}")

            # 2. Project Capacity Constraints (Min and Max)
            for p in projects:
                assigned_count = gp.quicksum(x[s.id, p.id] for s in students)
                m.addConstr(assigned_count >= p.capacity_min, name=f"cap_min_{p.id}")
                m.addConstr(assigned_count <= p.capacity_max, name=f"cap_max_{p.id}")

            # 3. Incompatibility Constraints
            # If student A and B are incompatible, they cannot be in the same project
            # x[A, p] + x[B, p] <= 1 for all p
            processed_pairs = set()
            for s1 in students:
                for s2_id in s1.incompatible_with:
                    # Avoid adding duplicate constraints for (A, B) and (B, A)
                    pair = tuple(sorted((s1.id, s2_id)))
                    if pair in processed_pairs:
                        continue
                    
                    # Find the student object for s2_id
                    s2 = next((s for s in students if s.id == s2_id), None)
                    if s2:
                        processed_pairs.add(pair)
                        for p in projects:
                            m.addConstr(x[s1.id, p.id] + x[s2.id, p.id] <= 1, name=f"incomp_{s1.id}_{s2.id}_{p.id}")

            # --- Optimize ---
            m.optimize()

            # --- Process Results ---
            status = m.Status
            if status == GRB.OPTIMAL:
                assignments = {p.id: [] for p in projects}
                student_assignments = {}
                
                for s in students:
                    for p in projects:
                        if x[s.id, p.id].X > 0.5:
                            assignments[p.id].append(s.id)
                            student_assignments[s.id] = p.id
                
                return AssignmentResult(
                    status="OPTIMAL",
                    objective_value=m.ObjVal,
                    assignments=assignments,
                    student_assignments=student_assignments,
                    solve_time=m.Runtime
                )
            elif status == GRB.INFEASIBLE:
                return AssignmentResult(
                    status="INFEASIBLE",
                    objective_value=0.0,
                    assignments={},
                    student_assignments={},
                    solve_time=m.Runtime
                )
            else:
                return AssignmentResult(
                    status=f"Status Code: {status}",
                    objective_value=0.0,
                    assignments={},
                    student_assignments={},
                    solve_time=m.Runtime if hasattr(m, 'Runtime') else 0.0
                )

        except gp.GurobiError as e:
            return AssignmentResult(
                status=f"Error: {str(e)}",
                objective_value=0.0,
                assignments={},
                student_assignments={},
                solve_time=0.0
            )
        except Exception as e:
             return AssignmentResult(
                status=f"Error: {str(e)}",
                objective_value=0.0,
                assignments={},
                student_assignments={},
                solve_time=0.0
            )
