"""
Utilitaires pour la validation et la manipulation de données.
"""

import json
from typing import Dict, List, Tuple, Any
import numpy as np


def validate_composition(composition: Dict[str, float]) -> Tuple[bool, List[str]]:
    """
    Valide une composition chimique.
    
    Args:
        composition: Dictionnaire {élément: pourcentage}
        
    Returns:
        Tuple (valide, liste_erreurs)
    """
    errors = []
    
    # Vérifier que tous les pourcentages sont positifs
    for element, percentage in composition.items():
        if percentage < 0:
            errors.append(f"Pourcentage négatif pour {element}: {percentage}")
        if percentage > 100:
            errors.append(f"Pourcentage supérieur à 100% pour {element}: {percentage}")
    
    # Vérifier que la somme ne dépasse pas 100%
    total = sum(composition.values())
    if total > 100.1:  # Petite tolérance
        errors.append(f"Somme des pourcentages dépasse 100%: {total:.2f}%")
    
    return len(errors) == 0, errors


def calculate_alloy_properties(composition: Dict[str, float], 
                             materials_data: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    Calcule les propriétés estimées d'un alliage basées sur sa composition.
    
    Args:
        composition: Composition finale {élément: pourcentage}
        materials_data: Données des matières premières utilisées
        
    Returns:
        Dictionnaire des propriétés calculées
    """
    properties = {}
    
    # Densité moyenne pondérée
    if composition:
        # Simplification: utiliser des densités moyennes d'éléments
        element_densities = {
            'Fe': 7.87, 'Ni': 8.91, 'Cr': 7.19, 'Mo': 10.28,
            'C': 2.27, 'Mn': 7.44, 'Si': 2.33, 'Al': 2.70,
            'Cu': 8.96, 'Ti': 4.51, 'V': 6.11, 'W': 19.25
        }
        
        total_density = 0
        total_mass_fraction = 0
        
        for element, percentage in composition.items():
            if element in element_densities and percentage > 0:
                density = element_densities[element]
                mass_fraction = percentage / 100.0
                total_density += mass_fraction / density
                total_mass_fraction += mass_fraction
        
        if total_mass_fraction > 0 and total_density > 0:
            properties['density'] = total_mass_fraction / total_density
    
    # Estimation de la dureté (formule simplifiée pour l'acier inoxydable)
    if 'Fe' in composition and 'Cr' in composition:
        fe_content = composition.get('Fe', 0)
        cr_content = composition.get('Cr', 0)
        ni_content = composition.get('Ni', 0)
        c_content = composition.get('C', 0)
        
        # Formule empirique simplifiée
        estimated_hardness = (
            fe_content * 0.3 +
            cr_content * 1.2 +
            ni_content * 0.8 +
            c_content * 50.0
        )
        properties['estimated_hardness_hrc'] = min(estimated_hardness, 65)
    
    # Point de fusion estimé
    if composition:
        # Points de fusion des éléments purs (°C)
        melting_points = {
            'Fe': 1538, 'Ni': 1455, 'Cr': 1907, 'Mo': 2623,
            'C': 3550, 'Mn': 1246, 'Si': 1414, 'Al': 660,
            'Cu': 1085, 'Ti': 1668, 'V': 1910, 'W': 3414
        }
        
        # Moyenne pondérée simplifiée
        weighted_mp = 0
        total_weight = 0
        
        for element, percentage in composition.items():
            if element in melting_points and percentage > 0:
                mp = melting_points[element]
                weight = percentage / 100.0
                weighted_mp += mp * weight
                total_weight += weight
        
        if total_weight > 0:
            properties['estimated_melting_point'] = weighted_mp / total_weight
    
    return properties


def format_currency(amount: float, currency: str = "€") -> str:
    """Formate un montant monétaire."""
    return f"{amount:,.2f} {currency}"


def format_percentage(value: float, decimals: int = 2) -> str:
    """Formate un pourcentage."""
    return f"{value:.{decimals}f}%"


def format_weight(weight: float, unit: str = "kg") -> str:
    """Formate un poids avec l'unité appropriée."""
    if weight >= 1000:
        return f"{weight/1000:.2f} t"
    elif weight >= 1:
        return f"{weight:.2f} kg"
    else:
        return f"{weight*1000:.0f} g"


def export_results_to_csv(result_data: Dict[str, Any], filename: str):
    """
    Exporte les résultats vers un fichier CSV.
    
    Args:
        result_data: Données des résultats
        filename: Nom du fichier CSV
    """
    import csv
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # En-tête
        writer.writerow(['Paramètre', 'Valeur', 'Unité'])
        
        # Informations générales
        if 'status' in result_data:
            writer.writerow(['Statut', result_data['status'], ''])
        if 'total_cost' in result_data:
            writer.writerow(['Coût Total', f"{result_data['total_cost']:.2f}", '€'])
        if 'total_weight' in result_data:
            writer.writerow(['Poids Total', f"{result_data['total_weight']:.2f}", 'kg'])
        if 'solve_time' in result_data:
            writer.writerow(['Temps de Résolution', f"{result_data['solve_time']:.3f}", 's'])
        
        # Ligne vide
        writer.writerow([])
        writer.writerow(['Matière Première', 'Quantité', 'Unité'])
        
        # Solution détaillée
        if 'solution' in result_data:
            for material, quantity in result_data['solution'].items():
                writer.writerow([material, f"{quantity:.3f}", 'kg'])
        
        # Ligne vide
        writer.writerow([])
        writer.writerow(['Élément', 'Pourcentage', 'Unité'])
        
        # Composition chimique
        if 'element_percentages' in result_data:
            for element, percentage in result_data['element_percentages'].items():
                writer.writerow([element, f"{percentage:.3f}", '%'])


def generate_report_data(problem, result) -> Dict[str, Any]:
    """
    Génère un dictionnaire complet avec toutes les données pour le rapport.
    
    Args:
        problem: Objet BlendingProblem
        result: Objet OptimizationResult
        
    Returns:
        Dictionnaire avec toutes les données formatées
    """
    report_data = {
        'problem_info': {
            'name': problem.name,
            'alloy_name': problem.alloy_spec.name,
            'target_weight': problem.alloy_spec.target_weight,
            'max_impurities': problem.alloy_spec.max_impurities,
            'num_materials': len(problem.raw_materials),
            'num_elements': len(problem.alloy_spec.elements)
        },
        'materials_info': [
            {
                'name': material.name,
                'cost_per_kg': material.cost_per_kg,
                'availability': material.availability,
                'composition': material.composition
            }
            for material in problem.raw_materials
        ],
        'elements_info': [
            {
                'symbol': element.symbol,
                'name': element.name,
                'min_percent': element.min_percent,
                'max_percent': element.max_percent,
                'target_percent': element.target_percent
            }
            for element in problem.alloy_spec.elements
        ],
        'results': {
            'status': result.status,
            'objective_value': result.objective_value,
            'total_cost': result.total_cost,
            'total_weight': result.total_weight,
            'solve_time': result.solve_time,
            'solution': result.solution,
            'element_percentages': result.element_percentages,
            'constraints_satisfied': result.constraints_satisfied
        }
    }
    
    # Ajouter les propriétés calculées de l'alliage
    if result.element_percentages:
        alloy_props = calculate_alloy_properties(result.element_percentages, [])
        report_data['alloy_properties'] = alloy_props
    
    return report_data


class DataValidator:
    """Classe utilitaire pour la validation avancée des données."""
    
    @staticmethod
    def validate_material_data(materials: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
        """Valide une liste de matières premières."""
        errors = []
        
        # Vérifier les noms uniques
        names = [m.get('name', '') for m in materials]
        if len(names) != len(set(names)):
            errors.append("Les noms des matières premières doivent être uniques")
        
        # Vérifier chaque matière première
        for i, material in enumerate(materials):
            prefix = f"Matière première {i+1}"
            
            if not material.get('name', '').strip():
                errors.append(f"{prefix}: Le nom est requis")
            
            if material.get('cost_per_kg', 0) <= 0:
                errors.append(f"{prefix}: Le coût doit être positif")
            
            if material.get('availability', 0) <= 0:
                errors.append(f"{prefix}: La disponibilité doit être positive")
            
            composition = material.get('composition', {})
            is_valid, comp_errors = validate_composition(composition)
            if not is_valid:
                errors.extend([f"{prefix} - {error}" for error in comp_errors])
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_alloy_specification(alloy_spec: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Valide une spécification d'alliage."""
        errors = []
        
        if not alloy_spec.get('name', '').strip():
            errors.append("Le nom de l'alliage est requis")
        
        if alloy_spec.get('target_weight', 0) <= 0:
            errors.append("Le poids cible doit être positif")
        
        elements = alloy_spec.get('elements', [])
        if not elements:
            errors.append("Au moins un élément doit être spécifié")
        
        # Vérifier chaque élément
        element_symbols = set()
        for i, element in enumerate(elements):
            prefix = f"Élément {i+1}"
            
            symbol = element.get('symbol', '').strip()
            if not symbol:
                errors.append(f"{prefix}: Le symbole est requis")
            elif symbol in element_symbols:
                errors.append(f"{prefix}: Symbole {symbol} déjà utilisé")
            else:
                element_symbols.add(symbol)
            
            min_percent = element.get('min_percent', 0)
            max_percent = element.get('max_percent', 100)
            
            if min_percent < 0:
                errors.append(f"{prefix}: Le pourcentage minimum ne peut pas être négatif")
            
            if max_percent > 100:
                errors.append(f"{prefix}: Le pourcentage maximum ne peut pas dépasser 100%")
            
            if min_percent > max_percent:
                errors.append(f"{prefix}: Le pourcentage minimum dépasse le maximum")
        
        return len(errors) == 0, errors