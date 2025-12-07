from dataclasses import dataclass, field
from typing import List, Dict, Optional

@dataclass
class Student:
    id: int
    name: str
    # Dictionary mapping project_id to preference score (higher is better)
    preferences: Dict[int, int] = field(default_factory=dict)
    # List of student IDs this student is incompatible with
    incompatible_with: List[int] = field(default_factory=list)

@dataclass
class Project:
    id: int
    name: str
    capacity_min: int
    capacity_max: int

@dataclass
class AssignmentResult:
    status: str  # 'OPTIMAL', 'INFEASIBLE', etc.
    objective_value: float
    # Map project_id to list of assigned student_ids
    assignments: Dict[int, List[int]]
    # Map student_id to assigned project_id
    student_assignments: Dict[int, int]
    solve_time: float
