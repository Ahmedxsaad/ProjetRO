# Modélisation Mathématique du Problème de Mélange d'Alliages

## 1. Formulation du Problème

Le problème de mélange d'alliages métallurgiques consiste à déterminer les proportions optimales de différentes matières premières pour obtenir un alliage final satisfaisant des spécifications de qualité au coût minimal.

## 2. Variables de Décision

Soit $I$ l'ensemble des matières premières disponibles, $i \in I = \{1, 2, ..., n\}$.

**Variables de décision :**
- $x_i$ : quantité de matière première $i$ à utiliser (en kg), $\forall i \in I$

## 3. Paramètres du Modèle

### 3.1 Paramètres de Coût
- $c_i$ : coût unitaire de la matière première $i$ (€/kg)
- $u_i$ : disponibilité maximale de la matière première $i$ (kg)

### 3.2 Paramètres de Composition
- $a_{ij}$ : pourcentage de l'élément chimique $j$ dans la matière première $i$ (%)
- $J$ : ensemble des éléments chimiques spécifiés
- $W$ : poids cible de l'alliage final (kg)

### 3.3 Spécifications de l'Alliage
- $L_j$ : pourcentage minimum requis de l'élément $j$ (%)
- $U_j$ : pourcentage maximum autorisé de l'élément $j$ (%)
- $T_j$ : pourcentage cible exact de l'élément $j$ (%) [optionnel]
- $M$ : pourcentage maximum d'impuretés autorisé (%)

## 4. Fonction Objectif

L'objectif est de minimiser le coût total de production :

$$\min Z = \sum_{i \in I} c_i \cdot x_i$$

## 5. Contraintes

### 5.1 Contrainte de Poids Total
Le poids total de l'alliage doit égaler le poids cible :
$$\sum_{i \in I} x_i = W$$

### 5.2 Contraintes de Composition Chimique
Pour chaque élément $j \in J$, la composition finale doit respecter les limites spécifiées :

**Contrainte de minimum :**
$$\sum_{i \in I} a_{ij} \cdot x_i \geq L_j \cdot \sum_{i \in I} x_i$$

**Contrainte de maximum :**
$$\sum_{i \in I} a_{ij} \cdot x_i \leq U_j \cdot \sum_{i \in I} x_i$$

**Contrainte de cible exacte (si spécifiée) :**
$$\sum_{i \in I} a_{ij} \cdot x_i = T_j \cdot \sum_{i \in I} x_i$$

### 5.3 Contraintes de Disponibilité
La quantité utilisée de chaque matière première ne peut dépasser sa disponibilité :
$$x_i \leq u_i, \quad \forall i \in I$$

### 5.4 Contraintes de Non-négativité
$$x_i \geq 0, \quad \forall i \in I$$

### 5.5 Contrainte d'Impuretés (Optionnelle)
Le pourcentage total des éléments non spécifiés ne doit pas dépasser le seuil autorisé :
$$\sum_{i \in I} \sum_{k \notin J} a_{ik} \cdot x_i \leq M \cdot \sum_{i \in I} x_i$$

où $k \notin J$ représente les éléments non explicitement spécifiés (impuretés).

## 6. Reformulation Linéaire

Les contraintes de composition peuvent être reformulées pour éliminer la division :

**De :**
$$\frac{\sum_{i \in I} a_{ij} \cdot x_i}{\sum_{i \in I} x_i} \geq L_j$$

**Vers :**
$$\sum_{i \in I} a_{ij} \cdot x_i \geq L_j \cdot W$$

En utilisant la contrainte $\sum_{i \in I} x_i = W$.

## 7. Modèle Complet

$$
\begin{align}
\min \quad & Z = \sum_{i \in I} c_i \cdot x_i \\
\text{s.t.} \quad & \sum_{i \in I} x_i = W \\
& \sum_{i \in I} a_{ij} \cdot x_i \geq L_j \cdot W, \quad \forall j \in J \\
& \sum_{i \in I} a_{ij} \cdot x_i \leq U_j \cdot W, \quad \forall j \in J \\
& \sum_{i \in I} a_{ij} \cdot x_i = T_j \cdot W, \quad \forall j \in J \text{ avec cible exacte} \\
& x_i \leq u_i, \quad \forall i \in I \\
& x_i \geq 0, \quad \forall i \in I
\end{align}
$$

## 8. Extensions du Modèle

### 8.1 Contraintes de Qualité Avancées
**Dureté estimée :**
$$\sum_{i \in I} \sum_{j \in J} \beta_j \cdot a_{ij} \cdot x_i \geq H_{min} \cdot W$$

où $\beta_j$ sont les coefficients de contribution à la dureté.

**Point de fusion :**
$$\sum_{i \in I} \sum_{j \in J} \gamma_j \cdot a_{ij} \cdot x_i \geq T_{fusion} \cdot W$$

### 8.2 Contraintes Logistiques
**Nombre maximum de matières premières :**
$$\sum_{i \in I} y_i \leq N_{max}$$

avec $y_i \in \{0,1\}$ variable binaire et $x_i \leq M \cdot y_i$.

### 8.3 Contraintes Environnementales
**Émissions de CO2 :**
$$\sum_{i \in I} e_i \cdot x_i \leq E_{max}$$

où $e_i$ est l'empreinte carbone de la matière première $i$.

## 9. Analyse de Sensibilité

Après résolution, l'analyse de sensibilité fournit :

### 9.1 Prix Duaux (Shadow Prices)
- $\pi_W$ : coût marginal d'une unité de poids supplémentaire
- $\pi_j^L$ : coût marginal pour relaxer la contrainte minimum de l'élément $j$
- $\pi_j^U$ : bénéfice marginal pour relaxer la contrainte maximum de l'élément $j$

### 9.2 Coûts Réduits
- $\bar{c}_i$ : réduction de coût nécessaire pour que la matière première $i$ entre dans la solution

### 9.3 Intervalles de Variation
- Variation des coûts $c_i$ maintenant l'optimalité
- Variation des disponibilités $u_i$ maintenant la faisabilité

## 10. Complexité Computationnelle

Le problème est un programme linéaire avec :
- **Variables** : $n$ (nombre de matières premières)
- **Contraintes d'égalité** : $1 + |J_{target}|$ (poids + cibles exactes)
- **Contraintes d'inégalité** : $2|J| + n$ (bornes composition + disponibilités)

**Complexité** : Polynomiale (résolvable par méthode du simplexe ou points intérieurs)

## 11. Cas Particuliers

### 11.1 Problème Infaisable
Aucune combinaison ne peut satisfaire toutes les contraintes simultanément.
**Causes courantes :**
- Contraintes contradictoires sur la composition
- Disponibilités insuffisantes
- Spécifications trop strictes

### 11.2 Problème Non Borné
Le coût peut être réduit indéfiniment.
**Cause :** Matière première à coût négatif ou erreur de modélisation.

### 11.3 Solutions Dégénérées
Plusieurs solutions optimales existent.
**Gestion :** Critères secondaires ou preferences utilisateur.