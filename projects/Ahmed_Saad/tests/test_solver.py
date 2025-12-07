import unittest
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from model.data_models import Student, Project
from model.optimization_model import StudentAssignmentSolver
from model.mock_solver import MockSolver

# Check if Gurobi is available
try:
    import gurobipy
    GUROBI_AVAILABLE = True
except ImportError:
    GUROBI_AVAILABLE = False

class TestGurobiSolver(unittest.TestCase):
    def setUp(self):
        self.solver = StudentAssignmentSolver()

    @unittest.skipUnless(GUROBI_AVAILABLE, "Gurobi not installed")
    def test_simple_assignment(self):
        s1 = Student(id=1, name="Alice", preferences={101: 10, 102: 1})
        s2 = Student(id=2, name="Bob", preferences={101: 1, 102: 10})
        p1 = Project(id=101, name="Project A", capacity_min=1, capacity_max=1)
        p2 = Project(id=102, name="Project B", capacity_min=1, capacity_max=1)

        result = self.solver.solve([s1, s2], [p1, p2])
        self.assertEqual(result.status, "OPTIMAL")
        self.assertEqual(result.student_assignments[1], 101)
        self.assertEqual(result.student_assignments[2], 102)

class TestMockSolver(unittest.TestCase):
    def setUp(self):
        self.solver = MockSolver()

    def test_mock_assignment(self):
        s1 = Student(id=1, name="Alice", preferences={101: 10})
        s2 = Student(id=2, name="Bob", preferences={102: 10})
        p1 = Project(id=101, name="Project A", capacity_min=1, capacity_max=1)
        p2 = Project(id=102, name="Project B", capacity_min=1, capacity_max=1)

        result = self.solver.solve([s1, s2], [p1, p2])
        
        # Mock solver might not be optimal, but should assign if possible
        self.assertIn("MOCK", result.status)
        self.assertEqual(len(result.student_assignments), 2)

if __name__ == '__main__':
    unittest.main()
