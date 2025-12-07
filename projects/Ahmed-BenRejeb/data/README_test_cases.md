# Test Cases - Mélange d'Alliages Métallurgiques

Ce dossier contient plusieurs cas de test complexes pour l'application d'optimisation de mélange d'alliages.

## Cas de Test Disponibles

### 1. Acier Inoxydable 316L - Grade Médical/Alimentaire
**Fichier**: `steel_316L_medical.json`
- **Application**: Équipements chimiques et pharmaceutiques
- **Complexité**: Moyenne - 6 matières premières, 7 éléments
- **Spécificités**: Contraintes strictes sur le carbone (≤ 0.08%), molybdène requis
- **Coût estimé**: ~2500-3000 € pour 1000 kg

### 2. Alliage d'Aluminium 7075-T6 - Grade Aéronautique  
**Fichier**: `aluminum_7075_aerospace.json`
- **Application**: Structures d'avions haute résistance
- **Complexité**: Élevée - 6 matières premières, 8 éléments
- **Spécificités**: Zinc principal élément d'alliage, contraintes serrées
- **Coût estimé**: ~1800-2200 € pour 500 kg

### 3. Acier à Outils M2 - Haute Vitesse
**Fichier**: `tool_steel_m2.json`  
- **Application**: Outils de coupe (fraises, forets)
- **Complexité**: Très élevée - 7 matières premières, 7 éléments
- **Spécificités**: Tungstène et vanadium coûteux, contraintes de dureté
- **Coût estimé**: ~8000-12000 € pour 800 kg

### 4. Superalliage Inconel 718 - Turbomachines
**Fichier**: `inconel_718_turbine.json`
- **Application**: Aubes de turbines, industrie nucléaire
- **Complexité**: Extrême - 8 matières premières, 9 éléments  
- **Spécificités**: Niobium rare et cher, cibles exactes pour plusieurs éléments
- **Coût estimé**: ~25000-30000 € pour 1200 kg

## Utilisation des Cas de Test

### Chargement dans l'Application
1. Lancer l'application: `python src/main.py`
2. Cliquer sur "📂 Charger" dans la barre d'outils
3. Sélectionner le fichier JSON du cas de test désiré
4. L'interface se remplit automatiquement avec les données

### Tests de Validation

#### Niveau Débutant - 316L
- **Objectif**: Vérifier le bon fonctionnement de base
- **Résultat attendu**: Solution optimale trouvée rapidement (< 1s)
- **Contraintes**: Toutes satisfaites avec marge

#### Niveau Intermédiaire - 7075 et M2  
- **Objectif**: Tester la gestion de contraintes multiples
- **Résultat attendu**: Solution optimale avec compromis
- **Contraintes**: Certaines à la limite (active constraints)

#### Niveau Avancé - Inconel 718
- **Objectif**: Tester les limites du solveur
- **Résultat attendu**: Solution optimale ou proche de l'optimal
- **Contraintes**: Très serrées, analysis de sensibilité importante

## Métriques de Performance

### Temps de Résolution Attendus
- **316L**: < 1 seconde  
- **7075**: 1-3 secondes
- **M2**: 2-5 secondes
- **Inconel 718**: 3-10 secondes

### Validation des Résultats

#### Vérifications Automatiques
- Toutes les contraintes de composition respectées
- Poids total = poids cible (à 1e-6 près)
- Somme des pourcentages ≈ 100%
- Respect des disponibilités

#### Vérifications Manuelles  
- Coût total cohérent avec les prix du marché
- Composition finale réaliste
- Utilisation préférentielle des matières premières moins chères

## Extensions Possibles

### Contraintes Additionnelles
- Contraintes environnementales (émissions CO2)
- Contraintes logistiques (nombre de fournisseurs max)
- Contraintes de qualité (homogénéité du mélange)

### Cas de Test Supplémentaires
- Bronzes spéciaux (naval, artistique)
- Aciers électriques (transformateurs)
- Alliages magnétiques (aimants permanents)
- Alliages à mémoire de forme (Nitinol)

## Notes Techniques

### Format des Données
- **Composition**: Pourcentages en poids
- **Disponibilité**: En kilogrammes
- **Coût**: En euros par kilogramme  
- **Densité**: En g/cm³

### Conventions de Nommage
- Symboles chimiques standards (Fe, Ni, Cr, etc.)
- Noms commerciaux pour les matières premières
- Grades standards de l'industrie