"""
Modèle d'optimisation pour le problème de mélange d'alliages métallurgiques.

Ce module implémente la formulation mathématique du problème de programmation linéaire
pour optimiser le coût du mélange tout en respectant les contraintes de composition.

Modélisation mathématique:

Variables de décision:
- x_i : quantité de matière première i à utiliser (kg)

Fonction objectif:
Minimiser: Σ(c_i * x_i) où c_i est le coût par kg de la matière première i

Contraintes:
1. Contraintes de composition:
   Pour chaque élément j: min_j ≤ (Σ(a_ij * x_i) / Σ(x_i)) * 100 ≤ max_j
   où a_ij est le pourcentage de l'élément j dans la matière première i

2. Contrainte de poids total:
   Σ(x_i) = target_weight

3. Contraintes de disponibilité:
   x_i ≤ availability_i

4. Non-négativité:
   x_i ≥ 0
"""

# Import Gurobi avec fallback vers mock
try:
    import gurobipy as gp
    from gurobipy import GRB
    GUROBI_AVAILABLE = True
except ImportError:
    # Utiliser le mock si Gurobi n'est pas disponible
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    import mock_gurobi as gp
    GRB = gp.GRB
    GUROBI_AVAILABLE = False
    print("⚠️ Gurobi non disponible, utilisation du mode simulation")

from typing import Dict, List, Tuple, Optional
from .data_model import BlendingProblem, RawMaterial, Element
from dataclasses import dataclass
import time


@dataclass
class OptimizationResult:
    """Résultats de l'optimisation."""
    status: str                          # Statut de la résolution
    objective_value: Optional[float]     # Valeur optimale de la fonction objectif
    solution: Dict[str, float]          # Solution optimale {matière_première: quantité}
    element_percentages: Dict[str, float]  # Pourcentages finaux des éléments
    solve_time: float                   # Temps de résolution
    total_weight: float                 # Poids total de l'alliage
    total_cost: float                   # Coût total
    constraints_satisfied: Dict[str, bool]  # État des contraintes
    sensitivity_analysis: Optional[Dict] = None  # Analyse de sensibilité


class BlendingOptimizer:
    """Optimiseur pour le problème de mélange d'alliages."""
    
    def __init__(self, problem: BlendingProblem):
        self.problem = problem
        self.model = None
        self.variables = {}
        
    def build_model(self) -> gp.Model:
        """Construit le modèle Gurobi pour le problème."""
        # Créer le modèle
        self.model = gp.Model("AlloyBlending")
        self.model.setParam('OutputFlag', 0)  # Désactiver les logs par défaut
        
        # Variables de décision: quantité de chaque matière première
        self.variables = {}
        for i, material in enumerate(self.problem.raw_materials):
            var_name = f"x_{material.name}"
            self.variables[material.name] = self.model.addVar(
                lb=0,  # Non-négativité
                ub=material.availability,  # Disponibilité
                name=var_name,
                vtype=GRB.CONTINUOUS
            )
        
        # Fonction objectif: minimiser le coût total
        objective = gp.quicksum(
            material.cost_per_kg * self.variables[material.name]
            for material in self.problem.raw_materials
        )
        self.model.setObjective(objective, GRB.MINIMIZE)
        
        # Contrainte de poids total
        total_weight = gp.quicksum(
            self.variables[material.name]
            for material in self.problem.raw_materials
        )
        self.model.addConstr(
            total_weight == self.problem.alloy_spec.target_weight,
            name="total_weight"
        )
        
        # Contraintes de composition pour chaque élément
        for element in self.problem.alloy_spec.elements:
            self._add_element_constraints(element)
            
        # Contraintes additionnelles (impuretés, etc.)
        self._add_additional_constraints()
        
        return self.model
    
    def _add_element_constraints(self, element: Element):
        """Ajoute les contraintes de composition pour un élément."""
        element_content = gp.quicksum(
            material.get_element_content(element.symbol) / 100.0 * 
            self.variables[material.name]
            for material in self.problem.raw_materials
        )
        
        total_weight = gp.quicksum(
            self.variables[material.name]
            for material in self.problem.raw_materials
        )
        
        # Contrainte minimum
        if element.min_percent > 0:
            self.model.addConstr(
                element_content >= element.min_percent / 100.0 * total_weight,
                name=f"min_{element.symbol}"
            )
        
        # Contrainte maximum
        if element.max_percent < 100:
            self.model.addConstr(
                element_content <= element.max_percent / 100.0 * total_weight,
                name=f"max_{element.symbol}"
            )
        
        # Contrainte cible exacte si spécifiée
        if element.target_percent is not None:
            self.model.addConstr(
                element_content == element.target_percent / 100.0 * total_weight,
                name=f"target_{element.symbol}"
            )
    
    def _add_additional_constraints(self):
        """Ajoute des contraintes supplémentaires selon le problème."""
        # Contrainte d'impuretés maximales
        if self.problem.alloy_spec.max_impurities < 100:
            # Calculer le total des éléments spécifiés
            specified_elements = {e.symbol for e in self.problem.alloy_spec.elements}
            
            impurities_content = gp.quicksum(
                material.get_element_content(element_symbol) / 100.0 * 
                self.variables[material.name]
                for material in self.problem.raw_materials
                for element_symbol in material.composition
                if element_symbol not in specified_elements
            )
            
            total_weight = gp.quicksum(
                self.variables[material.name]
                for material in self.problem.raw_materials
            )
            
            self.model.addConstr(
                impurities_content <= self.problem.alloy_spec.max_impurities / 100.0 * total_weight,
                name="max_impurities"
            )
        
        # Contraintes de qualité supplémentaires peuvent être ajoutées ici
        # (dureté, point de fusion, etc.)
    
    def solve(self) -> OptimizationResult:
        """Résout le problème d'optimisation."""
        if self.model is None:
            self.build_model()
        
        start_time = time.time()
        
        try:
            # Résoudre le modèle
            self.model.optimize()
            solve_time = time.time() - start_time
            
            # Analyser les résultats
            if self.model.status == GRB.OPTIMAL:
                result = self._extract_optimal_solution(solve_time)
                
                # Ajouter un avertissement si on utilise le mock
                if not GUROBI_AVAILABLE:
                    result.status = "SIMULATION (pas de Gurobi)"
                
                return result
            elif self.model.status == GRB.INFEASIBLE:
                return OptimizationResult(
                    status="INFAISABLE",
                    objective_value=None,
                    solution={},
                    element_percentages={},
                    solve_time=solve_time,
                    total_weight=0,
                    total_cost=0,
                    constraints_satisfied={}
                )
            elif self.model.status == GRB.UNBOUNDED:
                return OptimizationResult(
                    status="NON_BORNE",
                    objective_value=None,
                    solution={},
                    element_percentages={},
                    solve_time=solve_time,
                    total_weight=0,
                    total_cost=0,
                    constraints_satisfied={}
                )
            else:
                return OptimizationResult(
                    status=f"ERREUR_STATUT_{self.model.status}",
                    objective_value=None,
                    solution={},
                    element_percentages={},
                    solve_time=solve_time,
                    total_weight=0,
                    total_cost=0,
                    constraints_satisfied={}
                )
                
        except Exception as e:
            solve_time = time.time() - start_time
            error_msg = f"ERREUR: {str(e)}"
            if not GUROBI_AVAILABLE:
                error_msg += " (Mode simulation - installer Gurobi pour la résolution réelle)"
            
            return OptimizationResult(
                status=error_msg,
                objective_value=None,
                solution={},
                element_percentages={},
                solve_time=solve_time,
                total_weight=0,
                total_cost=0,
                constraints_satisfied={}
            )
    
    def _extract_optimal_solution(self, solve_time: float) -> OptimizationResult:
        """Extrait la solution optimale du modèle."""
        # Solution des variables
        solution = {}
        total_weight = 0
        total_cost = 0
        
        for material in self.problem.raw_materials:
            quantity = self.variables[material.name].X
            solution[material.name] = quantity
            total_weight += quantity
            total_cost += quantity * material.cost_per_kg
        
        # Calculer les pourcentages finaux des éléments
        element_percentages = {}
        all_elements = self.problem.get_all_elements()
        
        for element_symbol in all_elements:
            element_weight = sum(
                material.get_element_content(element_symbol) / 100.0 * solution[material.name]
                for material in self.problem.raw_materials
            )
            element_percentages[element_symbol] = (element_weight / total_weight * 100) if total_weight > 0 else 0
        
        # Vérifier la satisfaction des contraintes
        constraints_satisfied = self._check_constraints_satisfaction(element_percentages)
        
        return OptimizationResult(
            status="OPTIMAL",
            objective_value=self.model.objVal,
            solution=solution,
            element_percentages=element_percentages,
            solve_time=solve_time,
            total_weight=total_weight,
            total_cost=total_cost,
            constraints_satisfied=constraints_satisfied
        )
    
    def _check_constraints_satisfaction(self, element_percentages: Dict[str, float]) -> Dict[str, bool]:
        """Vérifie la satisfaction des contraintes."""
        constraints_satisfied = {}
        
        for element in self.problem.alloy_spec.elements:
            actual_percent = element_percentages.get(element.symbol, 0)
            
            # Vérifier les bornes
            min_satisfied = actual_percent >= element.min_percent - 1e-6
            max_satisfied = actual_percent <= element.max_percent + 1e-6
            
            constraints_satisfied[f"{element.symbol}_min"] = min_satisfied
            constraints_satisfied[f"{element.symbol}_max"] = max_satisfied
            
            # Vérifier la cible exacte si spécifiée
            if element.target_percent is not None:
                target_satisfied = abs(actual_percent - element.target_percent) <= 1e-6
                constraints_satisfied[f"{element.symbol}_target"] = target_satisfied
        
        return constraints_satisfied
    
    def perform_sensitivity_analysis(self) -> Dict:
        """Effectue une analyse de sensibilité sur le modèle résolu."""
        if self.model is None or self.model.status != GRB.OPTIMAL:
            return {}
        
        sensitivity = {
            'shadow_prices': {},
            'reduced_costs': {},
            'ranges': {}
        }
        
        # Prix duaux (shadow prices) des contraintes
        for constr in self.model.getConstrs():
            sensitivity['shadow_prices'][constr.ConstrName] = constr.Pi
        
        # Coûts réduits des variables
        for var in self.model.getVars():
            sensitivity['reduced_costs'][var.VarName] = var.RC
        
        return sensitivity