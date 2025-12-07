"""
Modèle de données pour le problème de mélange d'alliages métallurgiques.

Ce module définit les classes et structures de données nécessaires pour représenter
les matières premières, les spécifications d'alliage et les contraintes du problème.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass, field
import json


@dataclass
class Element:
    """Représente un élément chimique dans l'alliage."""
    symbol: str  # Symbole chimique (ex: Fe, C, Ni, Cr)
    name: str    # Nom de l'élément
    min_percent: float = 0.0    # Pourcentage minimum requis
    max_percent: float = 100.0  # Pourcentage maximum autorisé
    target_percent: Optional[float] = None  # Pourcentage cible si spécifié


@dataclass
class RawMaterial:
    """Représente une matière première disponible."""
    name: str                           # Nom de la matière première
    cost_per_kg: float                 # Coût par kg
    availability: float                # Disponibilité en kg
    composition: Dict[str, float]      # Composition chimique {symbole: pourcentage}
    density: float = 7.8               # Densité en g/cm³
    purity: float = 100.0              # Pureté en pourcentage
    
    def get_element_content(self, element_symbol: str) -> float:
        """Retourne le pourcentage d'un élément dans cette matière première."""
        return self.composition.get(element_symbol, 0.0)


@dataclass
class AlloySpecification:
    """Spécifications de l'alliage final à produire."""
    name: str                          # Nom de l'alliage
    target_weight: float               # Poids cible en kg
    elements: List[Element]            # Liste des éléments avec leurs contraintes
    max_impurities: float = 2.0        # Pourcentage maximum d'impuretés
    min_hardness: Optional[float] = None     # Dureté minimum HRC
    max_hardness: Optional[float] = None     # Dureté maximum HRC
    melting_point_min: Optional[float] = None  # Point de fusion minimum °C
    melting_point_max: Optional[float] = None  # Point de fusion maximum °C
    
    def get_element_by_symbol(self, symbol: str) -> Optional[Element]:
        """Retourne l'élément correspondant au symbole donné."""
        for element in self.elements:
            if element.symbol == symbol:
                return element
        return None


@dataclass 
class BlendingProblem:
    """Représente le problème complet de mélange d'alliages."""
    name: str
    raw_materials: List[RawMaterial]
    alloy_spec: AlloySpecification
    additional_constraints: Dict = field(default_factory=dict)
    
    def validate(self) -> List[str]:
        """Valide la cohérence du problème et retourne les erreurs."""
        errors = []
        
        # Vérifier que le poids cible est positif
        if self.alloy_spec.target_weight <= 0:
            errors.append("Le poids cible doit être positif")
            
        # Vérifier qu'il y a au moins une matière première
        if not self.raw_materials:
            errors.append("Au moins une matière première est requise")
            
        # Vérifier qu'il y a au moins un élément spécifié
        if not self.alloy_spec.elements:
            errors.append("Au moins un élément doit être spécifié")
            
        # Vérifier la cohérence des pourcentages
        for element in self.alloy_spec.elements:
            if element.min_percent > element.max_percent:
                errors.append(f"Pourcentage minimum supérieur au maximum pour {element.symbol}")
                
        return errors
    
    def get_all_elements(self) -> List[str]:
        """Retourne tous les symboles d'éléments présents dans le problème."""
        elements = set()
        
        # Éléments de la spécification
        for element in self.alloy_spec.elements:
            elements.add(element.symbol)
            
        # Éléments dans les matières premières
        for material in self.raw_materials:
            elements.update(material.composition.keys())
            
        return sorted(list(elements))
    
    def save_to_json(self, filepath: str):
        """Sauvegarde le problème dans un fichier JSON."""
        data = {
            'name': self.name,
            'raw_materials': [
                {
                    'name': rm.name,
                    'cost_per_kg': rm.cost_per_kg,
                    'availability': rm.availability,
                    'composition': rm.composition,
                    'density': rm.density,
                    'purity': rm.purity
                } for rm in self.raw_materials
            ],
            'alloy_spec': {
                'name': self.alloy_spec.name,
                'target_weight': self.alloy_spec.target_weight,
                'elements': [
                    {
                        'symbol': e.symbol,
                        'name': e.name,
                        'min_percent': e.min_percent,
                        'max_percent': e.max_percent,
                        'target_percent': e.target_percent
                    } for e in self.alloy_spec.elements
                ],
                'max_impurities': self.alloy_spec.max_impurities,
                'min_hardness': self.alloy_spec.min_hardness,
                'max_hardness': self.alloy_spec.max_hardness,
                'melting_point_min': self.alloy_spec.melting_point_min,
                'melting_point_max': self.alloy_spec.melting_point_max
            },
            'additional_constraints': self.additional_constraints
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    @classmethod
    def load_from_json(cls, filepath: str) -> 'BlendingProblem':
        """Charge un problème depuis un fichier JSON."""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Reconstruire les matières premières
        raw_materials = [
            RawMaterial(
                name=rm_data['name'],
                cost_per_kg=rm_data['cost_per_kg'],
                availability=rm_data['availability'],
                composition=rm_data['composition'],
                density=rm_data.get('density', 7.8),
                purity=rm_data.get('purity', 100.0)
            ) for rm_data in data['raw_materials']
        ]
        
        # Reconstruire les éléments
        elements = [
            Element(
                symbol=e_data['symbol'],
                name=e_data['name'],
                min_percent=e_data['min_percent'],
                max_percent=e_data['max_percent'],
                target_percent=e_data.get('target_percent')
            ) for e_data in data['alloy_spec']['elements']
        ]
        
        # Reconstruire la spécification d'alliage
        alloy_spec_data = data['alloy_spec']
        alloy_spec = AlloySpecification(
            name=alloy_spec_data['name'],
            target_weight=alloy_spec_data['target_weight'],
            elements=elements,
            max_impurities=alloy_spec_data.get('max_impurities', 2.0),
            min_hardness=alloy_spec_data.get('min_hardness'),
            max_hardness=alloy_spec_data.get('max_hardness'),
            melting_point_min=alloy_spec_data.get('melting_point_min'),
            melting_point_max=alloy_spec_data.get('melting_point_max')
        )
        
        return cls(
            name=data['name'],
            raw_materials=raw_materials,
            alloy_spec=alloy_spec,
            additional_constraints=data.get('additional_constraints', {})
        )