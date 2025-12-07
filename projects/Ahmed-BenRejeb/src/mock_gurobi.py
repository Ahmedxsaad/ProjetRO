"""
Mock Gurobi pour tester l'interface sans licence Gurobi.
Ce module simule les fonctionnalités de base de Gurobi pour le développement.
"""

import time
from typing import Dict, Any, Optional


class MockVariable:
    """Variable mock pour simuler gp.Var."""
    def __init__(self, name: str, lb: float = 0, ub: float = float('inf')):
        self.VarName = name
        self.lb = lb
        self.ub = ub
        self.X = 0.0  # Solution value
        self.RC = 0.0  # Reduced cost

    def __str__(self):
        return f"MockVar({self.VarName})"


class MockConstraint:
    """Contrainte mock pour simuler gp.Constr."""
    def __init__(self, name: str):
        self.ConstrName = name
        self.Pi = 0.0  # Shadow price

    def __str__(self):
        return f"MockConstr({self.ConstrName})"


class MockLinExpr:
    """Expression linéaire mock."""
    def __init__(self):
        self.constant = 0.0
        self.terms = {}  # var -> coefficient

    def __add__(self, other):
        if isinstance(other, (int, float)):
            result = MockLinExpr()
            result.constant = self.constant + other
            result.terms = self.terms.copy()
            return result
        elif isinstance(other, MockVariable):
            result = MockLinExpr()
            result.constant = self.constant
            result.terms = self.terms.copy()
            result.terms[other] = result.terms.get(other, 0) + 1
            return result
        elif isinstance(other, MockLinExpr):
            result = MockLinExpr()
            result.constant = self.constant + other.constant
            result.terms = self.terms.copy()
            for var, coeff in other.terms.items():
                result.terms[var] = result.terms.get(var, 0) + coeff
            return result
        return NotImplemented

    def __radd__(self, other):
        return self.__add__(other)

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            result = MockLinExpr()
            result.constant = self.constant * other
            result.terms = {var: coeff * other for var, coeff in self.terms.items()}
            return result
        return NotImplemented

    def __rmul__(self, other):
        return self.__mul__(other)


class MockModel:
    """Modèle d'optimisation mock."""
    
    # Constants pour les statuts
    OPTIMAL = 2
    INFEASIBLE = 3
    UNBOUNDED = 5
    
    # Constants pour les sens d'optimisation
    MINIMIZE = 1
    MAXIMIZE = -1
    
    # Types de variables
    CONTINUOUS = 'C'
    BINARY = 'B'
    INTEGER = 'I'
    
    def __init__(self, name: str = "MockModel"):
        self.ModelName = name
        self.status = None
        self.objVal = None
        self.variables = []
        self.constraints = []
        self.objective = None
        self.sense = self.MINIMIZE
        self._solved = False

    def setParam(self, param: str, value: Any):
        """Simule la configuration des paramètres."""
        pass

    def addVar(self, lb: float = 0, ub: float = float('inf'), 
               obj: float = 0, vtype: str = CONTINUOUS, name: str = "",
               column=None) -> MockVariable:
        """Ajoute une variable au modèle."""
        var = MockVariable(name, lb, ub)
        self.variables.append(var)
        return var

    def addConstr(self, lhs, sense: str = None, rhs: float = None, name: str = ""):
        """Ajoute une contrainte au modèle."""
        constr = MockConstraint(name)
        self.constraints.append(constr)
        return constr

    def setObjective(self, expr, sense: int = None):
        """Définit la fonction objectif."""
        self.objective = expr
        if sense is not None:
            self.sense = sense

    def optimize(self):
        """Simule la résolution du modèle."""
        time.sleep(0.1)  # Simuler le temps de calcul
        
        # Solution mock simpliste
        if len(self.variables) > 0:
            self.status = self.OPTIMAL
            self.objVal = 1000.0  # Coût fictif
            
            # Assigner des valeurs fictives aux variables
            total_weight = 1000.0  # Supposer un poids cible de 1000 kg
            weight_per_var = total_weight / len(self.variables)
            
            for i, var in enumerate(self.variables):
                # Distribuer le poids de façon décroissante
                var.X = weight_per_var * (1.0 - i * 0.1) if i < 10 else 0.0
                var.X = max(var.X, 0.0)  # Assurer la non-négativité
        else:
            self.status = self.INFEASIBLE
            self.objVal = None

        self._solved = True

    def getVars(self):
        """Retourne la liste des variables."""
        return self.variables

    def getConstrs(self):
        """Retourne la liste des contraintes."""
        return self.constraints

    def update(self):
        """Met à jour le modèle (nécessaire dans Gurobi réel)."""
        pass


def quicksum(expr_list):
    """Simule gp.quicksum()."""
    if not expr_list:
        return MockLinExpr()
    
    result = MockLinExpr()
    for expr in expr_list:
        if isinstance(expr, MockVariable):
            # Convertir variable en expression
            var_expr = MockLinExpr()
            var_expr.terms[expr] = 1.0
            result = result + var_expr
        elif isinstance(expr, (int, float)):
            result = result + expr
        elif isinstance(expr, MockLinExpr):
            result = result + expr
        else:
            # Supposer que c'est une multiplication
            result = result + expr
    
    return result


def Model(name: str = "MockModel"):
    """Crée un nouveau modèle mock."""
    return MockModel(name)


# Classes d'exceptions mock
class GurobiError(Exception):
    """Exception Gurobi mock."""
    def __init__(self, message: str, errno: int = 0):
        super().__init__(message)
        self.errno = errno


# Alias pour la compatibilité
GRB = MockModel